"""Normalization service for connector-specific raw objects."""

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.normalized_supporter import NormalizedSupporter
from app.models.raw_object import RawObject
from app.models.staging_gift import StagingGift


class NormalizationService:
    """Persist lightweight normalized read models for UI and reporting."""

    def normalize_raw_object(self, db: Session, raw_object: RawObject, payload: dict[str, Any]) -> None:
        """Normalize a raw OneCause object into read models."""
        if raw_object.source_system != "onecause":
            return
        if raw_object.external_object_type == "paid_activities":
            self._upsert_gift(db, raw_object, payload)
        if raw_object.external_object_type == "supporters":
            self._upsert_supporter(db, raw_object, payload)

    def list_gifts(self, db: Session, offset: int = 0, limit: int = 100) -> tuple[list[StagingGift], int]:
        items = list(db.scalars(select(StagingGift).order_by(StagingGift.id.desc()).offset(offset).limit(limit)))
        total = db.scalar(select(func.count()).select_from(StagingGift)) or 0
        return items, total

    def list_supporters(
        self,
        db: Session,
        offset: int = 0,
        limit: int = 100,
    ) -> tuple[list[NormalizedSupporter], int]:
        items = list(
            db.scalars(
                select(NormalizedSupporter)
                .order_by(NormalizedSupporter.id.desc())
                .offset(offset)
                .limit(limit)
            )
        )
        total = db.scalar(select(func.count()).select_from(NormalizedSupporter)) or 0
        return items, total

    def _upsert_gift(self, db: Session, raw_object: RawObject, payload: dict[str, Any]) -> None:
        record = db.scalar(select(StagingGift).where(StagingGift.raw_object_id == raw_object.id))
        donor_name = " ".join(filter(None, [payload.get("first_name"), payload.get("last_name")])) or None
        gift_date = self._parse_date(payload.get("completed"))
        memo_parts = [payload.get("challengeName"), payload.get("receiptNumber")]
        memo = " | ".join([part for part in memo_parts if part]) or None
        if record is None:
            record = StagingGift(raw_object_id=raw_object.id)
        record.gift_id = str(payload.get("id")) if payload.get("id") is not None else None
        record.source_channel = raw_object.source_channel
        record.source_system = raw_object.source_system
        record.source_file_id = payload.get("challengeId")
        record.donor_name = donor_name
        record.amount = self._to_decimal(payload.get("amount"))
        record.currency = payload.get("currencyCode") or "USD"
        record.gift_date = gift_date
        record.payment_type = "card_or_portal"
        record.gift_type = "donation"
        record.memo = memo
        record.raw_payload_ref = raw_object.raw_payload_ref
        record.status = payload.get("status") or raw_object.duplicate_status
        record.confidence_score = 0.95
        db.add(record)

    def _upsert_supporter(self, db: Session, raw_object: RawObject, payload: dict[str, Any]) -> None:
        record = db.scalar(
            select(NormalizedSupporter).where(NormalizedSupporter.raw_object_id == raw_object.id)
        )
        team = payload.get("team") or {}
        if record is None:
            record = NormalizedSupporter(raw_object_id=raw_object.id, source_id=raw_object.source_id)
        record.supporter_id = str(payload.get("id")) if payload.get("id") is not None else None
        record.user_id = str(payload.get("userId")) if payload.get("userId") is not None else None
        record.supporter_name = payload.get("name")
        record.team_id = str(payload.get("teamId")) if payload.get("teamId") is not None else None
        record.team_name = team.get("name") if isinstance(team, dict) else None
        record.donation_amount = self._to_decimal(payload.get("donationAmount"))
        record.donation_count = payload.get("donationCount")
        record.team_credit_amount = self._to_decimal(payload.get("teamCreditAmount"))
        record.team_credit_count = payload.get("teamCreditCount")
        record.total_points_earned = self._to_decimal(payload.get("totalPointsEarned"))
        record.event_id = str(payload.get("eventId")) if payload.get("eventId") is not None else None
        event_ids = payload.get("eventIds")
        record.event_ids = ",".join(str(item) for item in event_ids) if isinstance(event_ids, list) else None
        accepted = payload.get("accepted")
        record.accepted = str(accepted).lower() if accepted is not None else None
        db.add(record)

    def _to_decimal(self, value: Any) -> Decimal | None:
        if value is None or value == "":
            return None
        return Decimal(str(value))

    def _parse_date(self, value: Any):
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None

