"""Schemas for ingestion runs."""

from datetime import datetime
from typing import Any

from app.schemas.common import ORMModel


class IngestionRunRead(ORMModel):
    """Ingestion run response."""

    id: int
    source_id: int
    run_type: str
    trigger_type: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    records_fetched_count: int
    files_fetched_count: int
    duplicates_detected_count: int
    error_message: str | None
    cursor_state: dict[str, Any] | None
    metadata_json: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime

