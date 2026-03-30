"""Normalization tests."""

from datetime import UTC, datetime

from app.models.raw_object import RawObject
from app.services.normalization_service import NormalizationService


def test_normalizes_onecause_paid_activity(db_session) -> None:
    raw_object = RawObject(
        source_id=1,
        ingestion_run_id=1,
        source_channel="api",
        source_system="onecause",
        external_object_type="paid_activities",
        external_object_id="don-1",
        external_parent_id=None,
        fetched_at=datetime.now(tz=UTC),
        event_timestamp=datetime.now(tz=UTC),
        original_filename=None,
        content_type="application/json",
        checksum_sha256="abc",
        payload_storage_path="/tmp/test.json",
        raw_payload_ref="/tmp/test.json",
        metadata_json={},
        parse_status="metadata_extracted",
        duplicate_status="unique",
    )
    db_session.add(raw_object)
    db_session.commit()
    db_session.refresh(raw_object)

    payload = {
        "id": "don-1",
        "first_name": "Les",
        "last_name": "Turner",
        "amount": 125.50,
        "completed": "2026-03-30T10:00:00Z",
        "status": "succeeded",
        "challengeId": "challenge-1",
        "challengeName": "ALS Walk",
    }
    NormalizationService().normalize_raw_object(db_session, raw_object, payload)
    db_session.commit()

    gifts, total = NormalizationService().list_gifts(db_session)
    assert total == 1
    assert gifts[0].donor_name == "Les Turner"
    assert str(gifts[0].amount) == "125.50"

