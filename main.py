import logging
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from routes.upload import router as upload_router
from routes.auth import router as auth_router

from database.connection import engine, Base
from services.rate_limiter import InMemoryRateLimiter

# Models import — sab tables create hon
from models.table_model import (
    PDFMaster,
    PDFTemp,
    ExtractedData,
    RejectedUpload,
    User
)

# ===== Create Project Folders Automatically =====

Path("uploads").mkdir(exist_ok=True)
Path("uploads/accepted").mkdir(parents=True, exist_ok=True)
Path("uploads/rejected").mkdir(parents=True, exist_ok=True)
Path("uploads/rejected/blank").mkdir(parents=True, exist_ok=True)
Path("uploads/rejected/corrupted").mkdir(parents=True, exist_ok=True)
Path("uploads/rejected/protected").mkdir(parents=True, exist_ok=True)
Path("uploads/rejected/unsupported").mkdir(parents=True, exist_ok=True)

# Create Database Tables
Base.metadata.create_all(bind=engine)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("pdf_extractor")

app = FastAPI(title="PDF Extractor API")

rate_limiters = {
    "login": InMemoryRateLimiter(limit=5, window_seconds=60),
    "register": InMemoryRateLimiter(limit=3, window_seconds=60),
    "upload": InMemoryRateLimiter(limit=10, window_seconds=3600),
}

# CORS enable karo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes
app.include_router(upload_router, prefix="/api")
app.include_router(auth_router, prefix="/api/auth")


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    path = request.url.path
    if "/api/auth/login" in path:
        limiter = rate_limiters["login"]
        key = request.client.host if request.client else "unknown"
        if not limiter.allow(key):
            logger.warning("Rate limit exceeded for login from %s", key)
            return JSONResponse(status_code=429, content={"detail": "Too many login attempts. Please try again later."})
    elif "/api/auth/register" in path:
        limiter = rate_limiters["register"]
        key = request.client.host if request.client else "unknown"
        if not limiter.allow(key):
            logger.warning("Rate limit exceeded for register from %s", key)
            return JSONResponse(status_code=429, content={"detail": "Too many registration attempts. Please try again later."})
    elif "/api/upload" in path or "/api/bulk-upload" in path:
        limiter = rate_limiters["upload"]
        key = request.client.host if request.client else "unknown"
        if not limiter.allow(key):
            logger.warning("Rate limit exceeded for upload from %s", key)
            return JSONResponse(status_code=429, content={"detail": "Too many upload attempts. Please try again later."})

    response = await call_next(request)
    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception for %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

# PDF upload files serve karo
app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Health Check
@app.get("/health")
def health():
    return {"status": "ok"}


# Frontend serve karo
@app.get("/")
def home():
    logger.info("Serving home page")
    return FileResponse("frontend/index.html")