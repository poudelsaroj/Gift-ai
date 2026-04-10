"""Schemas for the operator console endpoints."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from app.schemas.common import ORMModel


class OperatorRunRead(ORMModel):
    """Compact ingestion-run shape for the operator console."""

    id: int
    source_id: int
    source_name: str
    source_system: str
    run_type: str
    trigger_type: str
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    records_fetched_count: int
    duplicates_detected_count: int
    error_message: str | None


class OperatorSourceSummaryRead(ORMModel):
    """Source summary tailored for operator workflows."""

    id: int
    source_name: str
    source_system: str
    acquisition_mode: str
    auth_type: str
    enabled: bool
    schedule: str | None
    parser_name: str | None
    dedupe_keys: list[str] | None
    notes: str | None
    config_json: dict
    created_at: datetime
    updated_at: datetime
    workflow_label: str
    primary_action_label: str
    supports_test_connection: bool
    supports_direct_trigger: bool
    supports_manual_upload: bool
    supports_scheduler: bool
    special_actions: list[str]
    latest_run: OperatorRunRead | None
    raw_object_count: int
    record_count: int
    gift_record_count: int
    raw_object_types: list[str]
    record_status_values: list[str]
    latest_record_date: date | None


class OperatorConsoleSummaryRead(ORMModel):
    """Global summary metrics for the operator console."""

    total_sources: int
    total_records: int
    total_gift_records: int
    total_raw_objects: int
    latest_run_at: datetime | None


class OperatorConsoleStateRead(ORMModel):
    """Aggregated operator-console state payload."""

    summary: OperatorConsoleSummaryRead
    sources: list[OperatorSourceSummaryRead]
    recent_runs: list[OperatorRunRead]


class OperatorRecordRead(ORMModel):
    """Canonical record shape enriched with source context for the UI."""

    id: int
    raw_object_id: int
    source_id: int
    source_name: str
    record_type: str | None
    source_record_id: str | None
    source_parent_id: str | None
    gift_id: str | None
    source_channel: str | None
    source_system: str | None
    source_file_id: str | None
    primary_name: str | None
    primary_email: str | None
    donor_name: str | None
    donor_email: str | None
    company_name: str | None
    amount: Decimal | None
    currency: str | None
    record_date: date | None
    gift_date: date | None
    payment_type: str | None
    gift_type: str | None
    campaign_id: str | None
    campaign_name: str | None
    challenge_id: str | None
    challenge_name: str | None
    related_entity_id: str | None
    related_entity_name: str | None
    participant_id: str | None
    participant_name: str | None
    team_id: str | None
    team_name: str | None
    charity_id: str | None
    receipt_number: str | None
    memo: str | None
    raw_payload_ref: str | None
    status: str | None
    duplicate_status: str | None
    confidence_score: float | None
    extra_metadata: dict | None
    created_at: datetime
    updated_at: datetime
