"""Schemas for source configuration APIs."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_serializer

from app.schemas.common import ORMModel
from app.utils.security import redact_config


class SourceConfigBase(BaseModel):
    """Shared source config fields."""

    source_name: str
    source_system: str
    acquisition_mode: str
    auth_type: str
    enabled: bool = True
    schedule: str | None = None
    config_json: dict[str, Any] = Field(default_factory=dict)
    parser_name: str | None = None
    dedupe_keys: list[str] | None = None
    notes: str | None = None


class SourceConfigCreate(SourceConfigBase):
    """Source create payload."""


class SourceConfigUpdate(BaseModel):
    """Source patch payload."""

    source_name: str | None = None
    enabled: bool | None = None
    schedule: str | None = None
    config_json: dict[str, Any] | None = None
    parser_name: str | None = None
    dedupe_keys: list[str] | None = None
    notes: str | None = None


class SourceConfigRead(SourceConfigBase, ORMModel):
    """Source config response."""

    id: int
    created_at: datetime
    updated_at: datetime

    @field_serializer("config_json")
    def serialize_config_json(self, value: dict[str, Any]) -> dict[str, Any]:
        """Redact secrets from source config responses."""
        return redact_config(value)


class SourceTestResponse(ORMModel):
    """Connection test response."""

    ok: bool
    source_id: int
    details: dict[str, Any]


class TriggerIngestionRequest(BaseModel):
    """Manual trigger request."""

    run_type: str = "incremental"
    trigger_type: str = "manual"
    object_types: list[str] | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None


class TriggerIngestionResponse(ORMModel):
    """Manual trigger response."""

    ingestion_run_id: int
    status: str
    records_fetched_count: int
    duplicates_detected_count: int
    cursor_state: dict[str, Any] | None = None
