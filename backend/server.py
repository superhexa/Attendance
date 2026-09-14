from dotenv import load_dotenv
from pathlib import Path
import os
load_dotenv(Path(__file__).parent / ".env")

import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from core import db, client, ensure_indexes, seed_admin
import routes_auth, routes_structure, routes_users, routes_timetable, routes_attendance, routes_dashboard, routes_import, routes_promotion, routes_signups

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("attendance")

app = FastAPI(title="نظام إدارة الحضور المدرسي", version="1.0.0")


@app.get("/api/")
async def root():
    return {"message": "School Attendance API", "status": "ok"}


@app.get("/api/health")
async def health():
    return {"status": "healthy"}


for module in (routes_auth, routes_structure, routes_users, routes_timetable, routes_attendance, routes_dashboard, routes_import, routes_promotion, routes_signups):
    app.include_router(module.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى."})


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[o.strip() for o in os.environ.get("CORS_ORIGINS", "*").split(",")],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    try:
        await ensure_indexes()
        await seed_admin()
        logger.info("Startup complete: indexes ensured, admin seeded.")
    except Exception as e:
        logger.exception("Startup error: %s", e)


@app.on_event("shutdown")
async def shutdown():
    client.close()
