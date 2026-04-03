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
    assert gifts[0].record_type == "gift"
    assert gifts[0].source_record_id == "don-1"
    assert gifts[0].primary_name == "Les Turner"
    assert gifts[0].campaign_name == "ALS Walk"

    records, records_total = NormalizationService().list_records(db_session)
    assert records_total == 1
    assert records[0].record_type == "gift"


def test_normalizes_onecause_supporter_into_canonical_records(db_session) -> None:
    raw_object = RawObject(
        source_id=1,
        ingestion_run_id=1,
        source_channel="api",
        source_system="onecause",
        external_object_type="supporters",
        external_object_id="sup-1",
        external_parent_id=None,
        fetched_at=datetime.now(tz=UTC),
        event_timestamp=datetime.now(tz=UTC),
        original_filename=None,
        content_type="application/json",
        checksum_sha256="def",
        payload_storage_path="/tmp/test-supporter.json",
        raw_payload_ref="/tmp/test-supporter.json",
        metadata_json={},
        parse_status="metadata_extracted",
        duplicate_status="unique",
    )
    db_session.add(raw_object)
    db_session.commit()
    db_session.refresh(raw_object)

    payload = {
        "id": "sup-1",
        "userId": "user-1",
        "name": "Fundraiser One",
        "teamId": "team-1",
        "team": {"name": "Team Blue"},
        "donationAmount": "255.25",
        "donationCount": 3,
        "teamCreditAmount": "200.00",
        "teamCreditCount": 2,
        "totalPointsEarned": "400.00",
        "eventId": "event-1",
        "eventIds": ["event-1", "event-2"],
        "accepted": "2026-03-30T12:00:00Z",
    }
    NormalizationService().normalize_raw_object(db_session, raw_object, payload)
    db_session.commit()

    records, total = NormalizationService().list_records(db_session)
    assert total == 1
    assert records[0].record_type == "supporter"
    assert records[0].source_record_id == "sup-1"
    assert records[0].primary_name == "Fundraiser One"
    assert str(records[0].amount) == "255.25"
    assert records[0].team_name == "Team Blue"
    assert records[0].extra_metadata["donation_count"] == 3
