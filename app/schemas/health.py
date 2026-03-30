"""Health schema."""

from app.schemas.common import ORMModel


class HealthResponse(ORMModel):
    """Health response."""

    status: str

