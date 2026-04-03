"""Canonical normalized record schemas."""

from datetime import date, datetime
from decimal import Decimal

from app.schemas.common import ORMModel


class NormalizedRecordRead(ORMModel):
    """Canonical normalized record response shared across sources."""

    id: int
    raw_object_id: int
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


class NormalizedGiftRead(NormalizedRecordRead):
    """Legacy gift-only response shape."""


class NormalizedSupporterRead(ORMModel):
    """Normalized supporter response."""

    id: int
    raw_object_id: int
    source_id: int
    supporter_id: str | None
    user_id: str | None
    supporter_name: str | None
    team_id: str | None
    team_name: str | None
    donation_amount: Decimal | None
    donation_count: int | None
    team_credit_amount: Decimal | None
    team_credit_count: int | None
    total_points_earned: Decimal | None
    event_id: str | None
    event_ids: str | None
    accepted: str | None
    created_at: datetime
    updated_at: datetime
