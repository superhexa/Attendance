"""Background job: reminds teachers — and substitute teachers — to take
attendance a configurable number of minutes after each lesson period starts.

Runs as a plain asyncio task started at app startup (see server.py). No new
process, cron, or dependency is required.

Flow per lesson, once its period has started today:
  - If a substitute is assigned to that exact class/period/date, the
    substitute gets notified `substitute_reminder_offset_minutes` after the
    period starts (default 20).
  - Otherwise the originally-scheduled teacher gets notified
    `attendance_reminder_offset_minutes` after the period starts (default 5).
  - Once attendance has been submitted (session locked) for that lesson, no
    more reminders are sent for it.
  - Each (date, timetable_id, kind) reminder is only ever sent once, tracked
    in the `attendance_reminders_sent` collection.

Both offsets and the on/off switch are editable by anyone with the
`settings.manage` permission (Settings page → PATCH /api/settings).
"""
import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from core import db, new_id, iso, get_settings, notify
from routes_substitutions import find_active_substitution

logger = logging.getLogger("attendance.reminders")

CHECK_INTERVAL_SECONDS = 30


def _weekday_sunday_based(dt: datetime) -> int:
    # Python weekday(): Mon=0..Sun=6 -> convert to Sun=0..Sat=6 (matches timetable.day_of_week)
    return (dt.weekday() + 1) % 7


def _minutes_since_midnight(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute


def _parse_hhmm(value) -> int:
    """Return minutes-since-midnight for an 'HH:MM' string, or -1 if invalid."""
    if not value or ":" not in str(value):
        return -1
    try:
        h, m = str(value).split(":")[:2]
        return int(h) * 60 + int(m)
    except (ValueError, TypeError):
        return -1


async def _already_sent(date_str: str, timetable_id: str, kind: str) -> bool:
    existing = await db.attendance_reminders_sent.find_one(
        {"date": date_str, "timetable_id": timetable_id, "kind": kind}, {"_id": 1}
    )
    return existing is not None


async def _mark_sent(date_str: str, timetable_id: str, kind: str):
    try:
        await db.attendance_reminders_sent.insert_one({
            "id": new_id(), "date": date_str, "timetable_id": timetable_id,
            "kind": kind, "sent_at": iso(),
        })
    except Exception:
        # Unique index violation = another tick already recorded it. Fine.
        pass


async def _send_reminder(entry: dict, date_str: str, kind: str, teacher_id: str):
    target_user = await db.users.find_one({"teacher_id": teacher_id}, {"_id": 0, "id": 1})
    if not target_user:
        # No account to notify (e.g. teacher hasn't signed up yet) — don't retry forever.
        await _mark_sent(date_str, entry["id"], kind)
        return

    subj = await db.subjects.find_one({"id": entry.get("subject_id")}, {"_id": 0, "name": 1})
    section = await db.sections.find_one({"id": entry.get("section_id")}, {"_id": 0, "name": 1})
    subj_name = (subj or {}).get("name", "")
    section_name = (section or {}).get("name", "")
    period = entry.get("period")

    if kind == "substitute":
        title = "تذكير حصة بديلة: سجّل الحضور"
        message = f"أنت المعلم البديل لحصة {subj_name} - شعبة {section_name} (الحصة {period}). يرجى تسجيل الحضور الآن."
    else:
        title = "حان وقت تسجيل الحضور"
        message = f"سجّل حضور حصة {subj_name} - شعبة {section_name} (الحصة {period})."

    await notify(target_user["id"], "attendance_reminder", title, message, meta={
        "type": "attendance_reminder",
        "timetable_id": entry["id"],
        "date": date_str,
        "section_id": entry.get("section_id"),
        "subject_id": entry.get("subject_id"),
        "period": period,
        "kind": kind,
    })
    await _mark_sent(date_str, entry["id"], kind)


async def check_and_send_reminders():
    settings = await get_settings()
    if not settings.get("attendance_reminder_enabled", True):
        return

    try:
        tz = ZoneInfo(settings.get("timezone") or "Asia/Amman")
    except Exception:
        tz = ZoneInfo("UTC")

    now_local = datetime.now(tz)
    dow = _weekday_sunday_based(now_local)
    date_str = now_local.strftime("%Y-%m-%d")
    now_minutes = _minutes_since_midnight(now_local)

    reg_offset = int(settings.get("attendance_reminder_offset_minutes", 5) or 0)
    sub_offset = int(settings.get("substitute_reminder_offset_minutes", 20) or 0)

    entries = await db.timetable.find(
        {"deleted": {"$ne": True}, "day_of_week": dow}, {"_id": 0}
    ).to_list(2000)

    for entry in entries:
        start_minutes = _parse_hhmm(entry.get("start_time"))
        if start_minutes < 0:
            continue
        elapsed = now_minutes - start_minutes
        if elapsed < 0:
            continue  # period hasn't started yet today

        session = await db.attendance_sessions.find_one(
            {"timetable_id": entry["id"], "date": date_str, "status": "locked"}, {"_id": 1}
        )
        if session:
            continue  # attendance already taken — nothing to remind about

        sub = await find_active_substitution(date_str, entry)
        if sub:
            kind, offset, teacher_id = "substitute", sub_offset, sub.get("substitute_teacher_id")
        else:
            kind, offset, teacher_id = "regular", reg_offset, entry.get("teacher_id")

        if not teacher_id or elapsed < offset:
            continue
        if await _already_sent(date_str, entry["id"], kind):
            continue

        await _send_reminder(entry, date_str, kind, teacher_id)


async def reminder_loop():
    """Runs forever (until cancelled at shutdown), checking every 30s."""
    while True:
        try:
            await check_and_send_reminders()
        except Exception:
            logger.exception("Attendance reminder check failed")
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)
