"""Schemas for raw objects."""

from datetime import datetime
from typing import Any

from app.schemas.common import ORMModel


class RawObjectRead(ORMModel):
    """Raw object response."""

    id: int
    source_id: int
    ingestion_run_id: int | None
    source_channel: str
    source_system: str
    external_object_type: str
    external_object_id: str | None
    external_parent_id: str | None
    fetched_at: datetime
    event_timestamp: datetime | None
    original_filename: str | None
    content_type: str | None
    checksum_sha256: str
    payload_storage_path: str
    raw_payload_ref: str | None
    metadata_json: dict[str, Any] | None
    parse_status: str
    duplicate_status: str
    duplicate_of_id: int | None
    dedupe_reason: str | None
    created_at: datetime
    updated_at: datetime


class RawObjectPayloadResponse(ORMModel):
    """Stored payload response."""

    raw_object_id: int
    payload: dict[str, Any] | str

