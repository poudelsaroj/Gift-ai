"""Duplicate detection service."""

from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from app.models.raw_object import RawObject


class DedupeDecision:
    """Value object describing a dedupe outcome."""

    def __init__(self, status: str, duplicate_of_id: int | None = None, reason: str | None = None) -> None:
        self.status = status
        self.duplicate_of_id = duplicate_of_id
        self.reason = reason


class DedupeService:
    """Pre-ingestion duplicate candidate detection."""

    def detect(self, db: Session, candidate: RawObject) -> DedupeDecision:
        """Compare a candidate raw object against existing records."""
        checksum_match = db.scalar(
            select(RawObject).where(
                RawObject.id != candidate.id,
                RawObject.checksum_sha256 == candidate.checksum_sha256,
            )
        )
        if checksum_match:
            return DedupeDecision("confirmed_duplicate", checksum_match.id, "checksum_sha256_match")

        external_id_match = db.scalar(
            select(RawObject).where(
                RawObject.id != candidate.id,
                RawObject.source_system == candidate.source_system,
                RawObject.external_object_id.is_not(None),
                RawObject.external_object_id == candidate.external_object_id,
            )
        )
        if external_id_match:
            return DedupeDecision(
                "confirmed_duplicate",
                external_id_match.id,
                "source_system_external_object_id_match",
            )

        # Filename matching is a file-level heuristic only. Extracted row-level JSON objects
        # often inherit the same filename and timestamps from a single import batch.
        if candidate.content_type != "application/json":
            filename_heuristic = db.scalar(
                select(RawObject).where(
                    RawObject.id != candidate.id,
                    RawObject.content_type != "application/json",
                    and_(
                        RawObject.original_filename.is_not(None),
                        RawObject.original_filename == candidate.original_filename,
                        or_(
                            RawObject.event_timestamp == candidate.event_timestamp,
                            RawObject.fetched_at == candidate.fetched_at,
                        ),
                    ),
                )
            )
            if filename_heuristic:
                return DedupeDecision(
                    "possible_duplicate",
                    filename_heuristic.id,
                    "filename_timestamp_heuristic",
                )

        return DedupeDecision("unique")
