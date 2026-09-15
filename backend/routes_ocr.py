"""OCR: Read Arabic attendance ledger photos with Gemini 2.5 Pro.

Teacher (or anyone with attendance.create) uploads a photo. We call
Gemini with a strict Arabic prompt asking for JSON, validate it, and
return an editable draft. The teacher MUST review + confirm before
records are saved via the normal attendance endpoint.
"""
import base64
import binascii
import json
import os
import re
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from core import db, new_id, iso, get_current_user, require, log_audit

from google import genai
from google.genai import types as genai_types

router = APIRouter(prefix="/api/ocr", tags=["ocr"])

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = "gemini-2.5-pro"


def _sniff_mime_type(raw: bytes) -> str:
    """Best-effort image mime type detection from magic bytes (data-URI prefix is stripped before we get here)."""
    if raw[:3] == b"\xff\xd8\xff":
        return "image/jpeg"
    if raw[:8] == b"\x89PNG\r\n\x1a\n":
        return "image/png"
    if raw[:6] in (b"GIF87a", b"GIF89a"):
        return "image/gif"
    if raw[:4] == b"RIFF" and raw[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


class OCRRow(BaseModel):
    student_number: Optional[str] = ""
    name: str
    status: str  # PRESENT|ABSENT|LATE|EXCUSED|LEFT_EARLY
    note: Optional[str] = ""


class OCRResult(BaseModel):
    rows: List[OCRRow] = []
    date: Optional[str] = None
    subject: Optional[str] = None
    section: Optional[str] = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class OCRRequest(BaseModel):
    image_base64: str

    @field_validator("image_base64")
    @classmethod
    def validate_b64(cls, v: str) -> str:
        v = re.sub(r"^data:image/[^;]+;base64,", "", v)
        try:
            raw = base64.b64decode(v, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("صورة غير صالحة") from exc
        if not raw or len(raw) > 15 * 1024 * 1024:
            raise ValueError("حجم الصورة كبير جدًا (الحد 15 ميغابايت)")
        return v


SYSTEM_PROMPT = """
أنت نظام دقيق لاستخراج بيانات سجل الحضور العربي من الصور.
اقرأ الجدول من اليمين إلى اليسار وحافظ على رقم الطالب والاسم كما يظهران.
لا تخمّن البيانات غير المقروءة. إذا كان الصف غير واضح، اترك القيمة كما تظهر
وأضف ملاحظة عربية، وخفّض confidence.

القواعد لتحويل حالات الحضور إلى الإنجليزية:
- حاضر / موجود / علامة صح / نقطة سوداء => PRESENT
- غائب / X / علامة غياب / علامة خطأ => ABSENT
- متأخر / تأخر => LATE
- بعذر / إجازة / مأذون => EXCUSED
- خروج مبكر / انصراف => LEFT_EARLY

أعد JSON صالحًا فقط، بدون Markdown ولا شرح ولا علامات ```.
""".strip()

USER_PROMPT = """
حلّل صورة سجل الحضور واستخرج جميع صفوف الطلاب.
أعد هذا الشكل بالضبط:
{
  "rows": [
    {"student_number": "...", "name": "...", "status": "PRESENT|ABSENT|LATE|EXCUSED|LEFT_EARLY", "note": "..."}
  ],
  "date": "YYYY-MM-DD أو null",
  "subject": "اسم المادة أو null",
  "section": "اسم الشعبة أو null",
  "confidence": 0.0
}
اجعل confidence رقمًا بين 0 و1 للثقة الكلية.
لا تضف مفاتيح أخرى. استخدم null للبيانات غير الموجودة.
""".strip()


def _parse_json(text: str) -> OCRResult:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        data = json.loads(cleaned)
        return OCRResult.model_validate(data)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"تعذّر تحليل استجابة النموذج: {exc}") from exc


@router.post("/attendance")
async def ocr_attendance(body: OCRRequest, request: Request,
                         user: dict = Depends(require("attendance.create", "attendance.edit"))):
    if not GEMINI_API_KEY:
        raise HTTPException(status_code=500, detail="مفتاح النموذج غير مضبوط")

    image_bytes = base64.b64decode(body.image_base64)
    mime_type = _sniff_mime_type(image_bytes)

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        response = await client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=[
                genai_types.Content(role="user", parts=[
                    genai_types.Part.from_text(text=USER_PROMPT),
                    genai_types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ]),
            ],
            config=genai_types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.0,
                max_output_tokens=4096,
            ),
        )
        response_text = response.text or ""
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"فشل الاتصال بنموذج OCR: {exc}") from exc

    result = _parse_json(response_text)

    # Try to auto-match student_number to existing students in DB
    for row in result.rows:
        row_data = row.model_dump()
        if row_data.get("student_number"):
            match = await db.students.find_one(
                {"student_number": row_data["student_number"], "deleted": {"$ne": True}},
                {"_id": 0, "id": 1, "full_name": 1, "section_id": 1, "grade_id": 1}
            )
            if match:
                row_data["_matched_student_id"] = match["id"]
                row_data["_db_name"] = match.get("full_name", "")
                row_data["_db_section_id"] = match.get("section_id")

    # Save a draft record (not committed to attendance yet — teacher must confirm)
    draft_id = new_id()
    await db.ocr_drafts.insert_one({
        "id": draft_id,
        "created_by": user["id"],
        "created_at": iso(),
        "result": result.model_dump(),
        "status": "pending_review",
    })
    await log_audit(user, "ocr.extract", "ocr_draft", draft_id,
                    new_value={"rows": len(result.rows), "confidence": result.confidence}, request=request)

    return {"draft_id": draft_id, **result.model_dump()}


class ConfirmBody(BaseModel):
    draft_id: str
    date: str  # YYYY-MM-DD
    section_id: str
    subject_id: Optional[str] = None
    timetable_id: Optional[str] = None
    rows: List[dict]  # [{ student_id, status, note?, arrival_time? }]


@router.post("/confirm")
async def ocr_confirm(body: ConfirmBody, request: Request,
                      user: dict = Depends(require("attendance.create", "attendance.edit"))):
    """After the teacher reviews and edits, commit records as attendance."""
    draft = await db.ocr_drafts.find_one({"id": body.draft_id})
    if not draft:
        raise HTTPException(status_code=404, detail="المسودة غير موجودة")

    section = await db.sections.find_one({"id": body.section_id, "deleted": {"$ne": True}})
    if not section:
        raise HTTPException(status_code=400, detail="الشعبة غير موجودة")

    if not body.rows:
        raise HTTPException(status_code=400, detail="لا توجد سجلات للاعتماد")

    inserted = 0
    updated = 0
    errors = []
    valid_statuses = {"PRESENT", "ABSENT", "LATE", "EXCUSED", "LEFT_EARLY"}
    for row in body.rows:
        sid = row.get("student_id")
        st = (row.get("status") or "").upper()
        if not sid or st not in valid_statuses:
            errors.append({"row": row, "reason": "بيانات ناقصة أو غير صالحة"})
            continue
        student = await db.students.find_one({"id": sid, "deleted": {"$ne": True}}, {"_id": 0, "id": 1})
        if not student:
            errors.append({"row": row, "reason": "الطالب غير موجود"})
            continue
        rec_key = {"student_id": sid, "date": body.date, "timetable_id": body.timetable_id or ""}
        rec_data = {
            **rec_key,
            "status": st,
            "note": (row.get("note") or "").strip(),
            "section_id": body.section_id,
            "subject_id": body.subject_id,
            "source": "ocr",
            "recorded_by": user["id"],
            "recorded_at": iso(),
        }
        existing = await db.attendance_records.find_one(rec_key)
        if existing:
            await db.attendance_records.update_one({"_id": existing["_id"]}, {"$set": rec_data})
            updated += 1
        else:
            rec_data["id"] = new_id()
            await db.attendance_records.insert_one(rec_data)
            inserted += 1

    await db.ocr_drafts.update_one({"id": body.draft_id}, {"$set": {
        "status": "confirmed",
        "confirmed_at": iso(),
        "confirmed_by": user["id"],
        "commit_summary": {"inserted": inserted, "updated": updated, "errors": len(errors)},
    }})
    await log_audit(user, "ocr.confirm", "ocr_draft", body.draft_id,
                    new_value={"inserted": inserted, "updated": updated, "errors": len(errors)}, request=request)

    return {"ok": True, "inserted": inserted, "updated": updated, "errors": errors}
