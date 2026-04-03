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
        if raw_object.source_system == "onecause":
            if raw_object.external_object_type == "paid_activities":
                self._upsert_gift(db, raw_object, payload)
            if raw_object.external_object_type == "supporters":
                self._upsert_supporter_record(db, raw_object, payload)
                self._upsert_supporter(db, raw_object, payload)
            return
        if raw_object.source_system == "everyorg" and raw_object.external_object_type in {
            "donation",
            "donation_export",
        }:
            self._upsert_everyorg_gift(db, raw_object, payload)
            return
        if raw_object.source_system == "pledge" and raw_object.external_object_type == "donations":
            self._upsert_pledge_gift(db, raw_object, payload)

    def list_gifts(self, db: Session, offset: int = 0, limit: int = 100) -> tuple[list[StagingGift], int]:
        items = list(
            db.scalars(
                select(StagingGift)
                .where(StagingGift.record_type == "gift")
                .order_by(StagingGift.id.desc())
                .offset(offset)
                .limit(limit)
            )
        )
        total = db.scalar(
            select(func.count()).select_from(StagingGift).where(StagingGift.record_type == "gift")
        ) or 0
        return items, total

    def list_records(self, db: Session, offset: int = 0, limit: int = 100) -> tuple[list[StagingGift], int]:
        items = list(
            db.scalars(select(StagingGift).order_by(StagingGift.id.desc()).offset(offset).limit(limit))
        )
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
        participant = payload.get("participant") or {}
        team = payload.get("team") or {}
        participant_name = participant.get("name") if isinstance(participant, dict) else None
        team_name = team.get("name") if isinstance(team, dict) else None
        memo_parts = [
            payload.get("designation"),
            payload.get("receiptNumber"),
            payload.get("donationRepeat"),
        ]
        memo = " | ".join([part for part in memo_parts if part]) or None
        if record is None:
            record = StagingGift(raw_object_id=raw_object.id)
        record.record_type = "gift"
        record.source_record_id = str(payload.get("id")) if payload.get("id") is not None else None
        record.source_parent_id = (
            str(payload.get("participantId")) if payload.get("participantId") is not None else None
        )
        record.gift_id = str(payload.get("id")) if payload.get("id") is not None else None
        record.source_channel = raw_object.source_channel
        record.source_system = raw_object.source_system
        record.source_file_id = payload.get("challengeId")
        record.primary_name = donor_name
        record.primary_email = payload.get("email")
        record.donor_name = donor_name
        record.donor_email = payload.get("email")
        record.company_name = payload.get("companyName")
        record.amount = self._to_decimal(payload.get("amount"))
        record.currency = payload.get("currencyCode") or "USD"
        record.record_date = gift_date
        record.gift_date = gift_date
        record.payment_type = "card_or_portal"
        record.gift_type = "donation"
        record.campaign_id = payload.get("challengeId")
        record.campaign_name = payload.get("challengeName")
        record.challenge_id = payload.get("challengeId")
        record.challenge_name = payload.get("challengeName")
        record.related_entity_id = (
            str(payload.get("participantId")) if payload.get("participantId") is not None else None
        )
        record.related_entity_name = participant_name
        record.participant_id = str(payload.get("participantId")) if payload.get("participantId") is not None else None
        record.participant_name = participant_name
        record.team_id = str(payload.get("teamId")) if payload.get("teamId") is not None else None
        record.team_name = team_name
        record.charity_id = str(payload.get("charityId")) if payload.get("charityId") is not None else None
        record.receipt_number = payload.get("receiptNumber")
        record.memo = memo
        record.raw_payload_ref = raw_object.raw_payload_ref
        record.status = payload.get("status") or raw_object.duplicate_status
        record.duplicate_status = raw_object.duplicate_status
        record.confidence_score = 0.95
        record.extra_metadata = {
            "is_company_donation": payload.get("isCompanyDonation"),
            "fake_email": payload.get("fakeEmail"),
            "fees_paid": payload.get("feesPaid"),
            "donation_repeat": payload.get("donationRepeat"),
            "team_participant_id": payload.get("teamParticipantId"),
        }
        db.add(record)

    def _upsert_supporter_record(self, db: Session, raw_object: RawObject, payload: dict[str, Any]) -> None:
        record = db.scalar(select(StagingGift).where(StagingGift.raw_object_id == raw_object.id))
        team = payload.get("team") or {}
        event_ids = payload.get("eventIds")
        event_ids_joined = ",".join(str(item) for item in event_ids) if isinstance(event_ids, list) else None
        accepted = payload.get("accepted")
        if record is None:
            record = StagingGift(raw_object_id=raw_object.id)

        record.record_type = "supporter"
        record.source_record_id = str(payload.get("id")) if payload.get("id") is not None else None
        record.source_parent_id = str(payload.get("userId")) if payload.get("userId") is not None else None
        record.gift_id = None
        record.source_channel = raw_object.source_channel
        record.source_system = raw_object.source_system
        record.source_file_id = (
            str(payload.get("eventId")) if payload.get("eventId") is not None else event_ids_joined
        )
        record.primary_name = payload.get("name")
        record.primary_email = None
        record.donor_name = None
        record.donor_email = None
        record.company_name = None
        record.amount = self._to_decimal(payload.get("donationAmount"))
        record.currency = "USD"
        record.record_date = self._parse_date(accepted)
        record.gift_date = None
        record.payment_type = None
        record.gift_type = "supporter"
        record.campaign_id = (
            str(payload.get("eventId")) if payload.get("eventId") is not None else event_ids_joined
        )
        record.campaign_name = None
        record.challenge_id = None
        record.challenge_name = None
        record.related_entity_id = str(payload.get("userId")) if payload.get("userId") is not None else None
        record.related_entity_name = payload.get("name")
        record.participant_id = str(payload.get("id")) if payload.get("id") is not None else None
        record.participant_name = payload.get("name")
        record.team_id = str(payload.get("teamId")) if payload.get("teamId") is not None else None
        record.team_name = team.get("name") if isinstance(team, dict) else None
        record.charity_id = None
        record.receipt_number = None
        record.memo = "supporter_profile"
        record.raw_payload_ref = raw_object.raw_payload_ref
        record.status = "active" if accepted else "pending"
        record.duplicate_status = raw_object.duplicate_status
        record.confidence_score = 0.9
        record.extra_metadata = {
            "user_id": payload.get("userId"),
            "donation_count": payload.get("donationCount"),
            "team_credit_amount": payload.get("teamCreditAmount"),
            "team_credit_count": payload.get("teamCreditCount"),
            "total_points_earned": payload.get("totalPointsEarned"),
            "event_id": payload.get("eventId"),
            "event_ids": event_ids,
            "accepted": accepted,
        }
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

    def _upsert_everyorg_gift(self, db: Session, raw_object: RawObject, payload: dict[str, Any]) -> None:
        record = db.scalar(select(StagingGift).where(StagingGift.raw_object_id == raw_object.id))
        if record is None:
            record = StagingGift(raw_object_id=raw_object.id)

        nonprofit = payload.get("toNonprofit") or {}
        fundraiser = payload.get("fromFundraiser") or {}
        donor_name = " ".join(filter(None, [payload.get("firstName"), payload.get("lastName")])) or None
        memo_parts = [
            payload.get("designation"),
            fundraiser.get("title") if isinstance(fundraiser, dict) else None,
            payload.get("partnerDonationId"),
        ]

        record.record_type = "gift"
        record.source_record_id = (
            str(payload.get("chargeId")) if payload.get("chargeId") is not None else None
        )
        record.source_parent_id = (
            str(fundraiser.get("id"))
            if isinstance(fundraiser, dict) and fundraiser.get("id") is not None
            else None
        )
        record.gift_id = str(payload.get("chargeId")) if payload.get("chargeId") is not None else None
        record.source_channel = raw_object.source_channel
        record.source_system = raw_object.source_system
        record.source_file_id = nonprofit.get("slug") if isinstance(nonprofit, dict) else None
        record.primary_name = donor_name
        record.primary_email = payload.get("email")
        record.donor_name = donor_name
        record.donor_email = payload.get("email")
        record.company_name = payload.get("companyName")
        record.amount = self._to_decimal(payload.get("amount"))
        record.currency = payload.get("currency")
        record.record_date = self._parse_date(payload.get("donationDate"))
        record.gift_date = self._parse_date(payload.get("donationDate"))
        record.payment_type = payload.get("paymentMethod")
        record.gift_type = "donation"
        record.campaign_id = fundraiser.get("slug") if isinstance(fundraiser, dict) else None
        record.campaign_name = fundraiser.get("title") if isinstance(fundraiser, dict) else None
        record.challenge_id = fundraiser.get("slug") if isinstance(fundraiser, dict) else None
        record.challenge_name = fundraiser.get("title") if isinstance(fundraiser, dict) else None
        record.related_entity_id = (
            str(fundraiser.get("id"))
            if isinstance(fundraiser, dict) and fundraiser.get("id") is not None
            else None
        )
        record.related_entity_name = fundraiser.get("title") if isinstance(fundraiser, dict) else None
        record.participant_id = (
            str(fundraiser.get("id"))
            if isinstance(fundraiser, dict) and fundraiser.get("id") is not None
            else None
        )
        record.participant_name = fundraiser.get("title") if isinstance(fundraiser, dict) else None
        record.team_id = None
        record.team_name = None
        record.charity_id = (
            str(nonprofit.get("id"))
            if isinstance(nonprofit, dict) and nonprofit.get("id") is not None
            else None
        )
        record.receipt_number = payload.get("partnerDonationId")
        record.memo = " | ".join([part for part in memo_parts if part]) or None
        record.raw_payload_ref = raw_object.raw_payload_ref
        record.status = raw_object.duplicate_status
        record.duplicate_status = raw_object.duplicate_status
        record.confidence_score = 0.98
        record.extra_metadata = {
            "frequency": payload.get("frequency"),
            "net_amount": payload.get("netAmount"),
            "nonprofit_name": nonprofit.get("name") if isinstance(nonprofit, dict) else None,
            "nonprofit_ein": nonprofit.get("ein") if isinstance(nonprofit, dict) else None,
        }
        db.add(record)

    def _upsert_pledge_gift(self, db: Session, raw_object: RawObject, payload: dict[str, Any]) -> None:
        record = db.scalar(select(StagingGift).where(StagingGift.raw_object_id == raw_object.id))
        if record is None:
            record = StagingGift(raw_object_id=raw_object.id)

        donor = self._first_dict(payload, "donor", "supporter", "user")
        organization = self._first_dict(payload, "organization", "nonprofit", "charity")
        fundraiser = self._first_dict(payload, "fundraiser", "campaign")
        donor_name = (
            self._first_value(donor, "name")
            or self._first_value(payload, "donor_name", "name")
            or " ".join(
                filter(
                    None,
                    [
                        self._first_value(donor, "first_name", "firstName"),
                        self._first_value(donor, "last_name", "lastName"),
                    ],
                )
            )
            or None
        )
        amount = self._first_value(payload, "amount", "gross_amount", "donation_amount")
        currency = self._first_value(payload, "currency", "currency_code") or "USD"
        donation_date = self._first_value(
            payload,
            "created_at",
            "paid_at",
            "donation_date",
            "createdAt",
            "paidAt",
            "donationDate",
        )

        record.record_type = "gift"
        record.source_record_id = str(
            self._first_value(payload, "id", "donation_id", "charge_id", "uuid") or ""
        ) or None
        record.source_parent_id = str(self._first_value(fundraiser, "id", "uuid") or "") or None
        record.gift_id = record.source_record_id
        record.source_channel = raw_object.source_channel
        record.source_system = raw_object.source_system
        record.source_file_id = str(self._first_value(organization, "id", "ngo_id", "uuid") or "") or None
        record.primary_name = donor_name
        record.primary_email = self._first_value(donor, "email") or self._first_value(payload, "email", "donor_email")
        record.donor_name = donor_name
        record.donor_email = record.primary_email
        record.company_name = self._first_value(payload, "company_name")
        record.amount = self._to_decimal(amount)
        record.currency = currency
        record.record_date = self._parse_date(donation_date)
        record.gift_date = self._parse_date(donation_date)
        record.payment_type = self._first_value(payload, "payment_method", "paymentMethod", "payment_type")
        record.gift_type = "donation"
        record.campaign_id = str(self._first_value(fundraiser, "id", "uuid") or "") or None
        record.campaign_name = self._first_value(fundraiser, "title", "name")
        record.challenge_id = record.campaign_id
        record.challenge_name = record.campaign_name
        record.related_entity_id = record.campaign_id
        record.related_entity_name = record.campaign_name
        record.participant_id = None
        record.participant_name = None
        record.team_id = None
        record.team_name = None
        record.charity_id = str(self._first_value(organization, "id", "ngo_id", "uuid") or "") or None
        record.receipt_number = str(self._first_value(payload, "receipt_number", "reference", "external_id") or "") or None
        record.memo = self._first_value(payload, "message", "designation", "note")
        record.raw_payload_ref = raw_object.raw_payload_ref
        record.status = "succeeded"
        record.duplicate_status = raw_object.duplicate_status
        record.confidence_score = 0.92
        record.extra_metadata = {
            "organization_name": self._first_value(organization, "name"),
            "organization_profile_url": self._first_value(organization, "profile_url"),
            "organization_ngo_id": self._first_value(organization, "ngo_id"),
            "fundraiser_name": self._first_value(fundraiser, "title", "name"),
        }
        db.add(record)

    def _to_decimal(self, value: Any) -> Decimal | None:
        if value is None or value == "":
            return None
        return Decimal(str(value))

    def _first_dict(self, payload: dict[str, Any], *keys: str) -> dict[str, Any]:
        for key in keys:
            value = payload.get(key)
            if isinstance(value, dict):
                return value
        return {}

    def _first_value(self, payload: dict[str, Any], *keys: str) -> Any:
        for key in keys:
            value = payload.get(key)
            if value not in (None, ""):
                return value
        return None

    def _parse_date(self, value: Any):
        if not isinstance(value, str):
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            return None
