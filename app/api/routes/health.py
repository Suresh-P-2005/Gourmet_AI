"""
Health check endpoint — server status, version, and uptime.
"""

import time
from fastapi import APIRouter
from app.core.config import get_settings
from app.models.response_models import HealthResponse

router = APIRouter(prefix="/api/health", tags=["Health"])

# Track server start time
_start_time = time.time()


@router.get(
    "",
    response_model=HealthResponse,
    summary="Health Check",
    description="Returns server status, version, and uptime.",
)
async def health_check():
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
        uptime_seconds=round(time.time() - _start_time, 2),
        gemini_configured=settings.GEMINI_API_KEY != "your_gemini_api_key_here",
    )
