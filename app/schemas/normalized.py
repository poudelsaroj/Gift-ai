"""Normalized read model schemas."""

from datetime import date, datetime
from decimal import Decimal

from app.schemas.common import ORMModel


class NormalizedGiftRead(ORMModel):
    """Normalized gift response."""

    id: int
    raw_object_id: int
    gift_id: str | None
    source_channel: str | None
    source_system: str | None
    source_file_id: str | None
    donor_name: str | None
    amount: Decimal | None
    currency: str | None
    gift_date: date | None
    payment_type: str | None
    gift_type: str | None
    memo: str | None
    raw_payload_ref: str | None
    status: str | None
    confidence_score: float | None
    created_at: datetime
    updated_at: datetime


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

