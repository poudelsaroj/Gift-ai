"""Dedupe tests."""

from datetime import UTC, datetime

from app.dedupe.service import DedupeService
from app.models.raw_object import RawObject


def build_raw_object(**overrides) -> RawObject:
    base = {
        "source_id": 1,
        "ingestion_run_id": 1,
        "source_channel": "api",
        "source_system": "onecause",
        "external_object_type": "paid_activities",
        "external_object_id": "123",
        "external_parent_id": None,
        "fetched_at": datetime.now(tz=UTC),
        "event_timestamp": datetime.now(tz=UTC),
        "original_filename": None,
        "content_type": "application/json",
        "checksum_sha256": "abc",
        "payload_storage_path": "/tmp/raw.json",
        "raw_payload_ref": "/tmp/raw.json",
        "metadata_json": {},
        "parse_status": "metadata_extracted",
        "duplicate_status": "unique",
    }
    base.update(overrides)
    return RawObject(**base)


def test_dedupe_detects_external_id_match(db_session) -> None:
    existing = build_raw_object()
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)

    candidate = build_raw_object(checksum_sha256="different", external_object_id="123")
    db_session.add(candidate)
    db_session.flush()

    decision = DedupeService().detect(db_session, candidate)
    assert decision.status == "confirmed_duplicate"
    assert decision.duplicate_of_id == existing.id

