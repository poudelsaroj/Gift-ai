"""Health endpoints."""

from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter()


@router.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Basic health endpoint."""
    return HealthResponse(status="ok")
