"""Health check endpoints."""

from fastapi import APIRouter
from app.core.config import get_settings
from app.db.schemas import HealthResponse

settings = get_settings()
router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION
    )
