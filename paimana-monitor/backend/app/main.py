"""
PAIMANA Intelligence Platform — FastAPI Application Entry Point
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import get_settings
from app.api import auth, projects, analytics, alerts, imports, admin

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION} [{settings.ENVIRONMENT}]")
    import os
    os.makedirs(settings.LOCAL_STORAGE_PATH, exist_ok=True)
    yield
    logger.info("Shutting down PAIMANA platform")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "PAIMANA Project Intelligence & Early Warning System — "
        "SIH 2026 Problem Statement 26103 | MoSPI / DIID"
    ),
    docs_url="/docs" if settings.API_DEBUG else None,
    redoc_url="/redoc" if settings.API_DEBUG else None,
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(imports.router)
app.include_router(admin.router)


# ─── Health ───────────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health_check():
    from sqlalchemy import text
    from app.database.connection import AsyncSessionLocal
    db_status = "disconnected"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception:
        pass
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "service": "paimana-api",
        "version": settings.APP_VERSION,
    }


# ─── Global error handler ─────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred. Please contact the system administrator.",
            "path": str(request.url.path),
        },
    )
