"""Gmail normalization tests."""

from datetime import UTC, datetime

from app.models.raw_object import RawObject
from app.models.staging_gift import StagingGift
from app.services.normalization_service import NormalizationService


def test_normalizes_gmail_gift_extract(db_session) -> None:
    raw_object = RawObject(
        source_id=1,
        ingestion_run_id=None,
        source_channel="email_extraction",
        source_system="gmail",
        external_object_type="gift_extract",
        external_object_id="gift-1",
        external_parent_id="msg-1",
        fetched_at=datetime(2026, 4, 6, tzinfo=UTC),
        event_timestamp=None,
        original_filename="gift-report.csv",
        content_type="application/json",
        checksum_sha256="abc123",
        payload_storage_path="raw_storage/gmail/gift-1.json",
        raw_payload_ref="raw_storage/gmail/gift-1.json",
        metadata_json={},
        parse_status="metadata_extracted",
        duplicate_status="unique",
        duplicate_of_id=None,
        dedupe_reason=None,
    )
    db_session.add(raw_object)
    db_session.commit()
    db_session.refresh(raw_object)

    payload = {
        "recordType": "gift",
        "sourceRecordId": "gift-1",
        "sourceParentId": "msg-1",
        "giftId": "gift-1",
        "sourceFileId": "gift-report.csv",
        "messageId": "msg-1",
        "sourceMedium": "attachment_csv",
        "sourceFilename": "gift-report.csv",
        "sourceAttachmentId": "att-1",
        "primaryName": "Jane Donor",
        "primaryEmail": "jane@example.org",
        "donorName": "Jane Donor",
        "donorEmail": "jane@example.org",
        "amount": "125.00",
        "currency": "USD",
        "recordDate": "2026-04-05",
        "giftDate": "2026-04-05",
        "campaignId": None,
        "campaignName": "Spring Appeal",
        "relatedEntityId": "msg-1",
        "relatedEntityName": "attachment_csv",
        "receiptNumber": "rcpt-1",
        "memo": "Imported from Gmail attachment",
        "paymentType": "email_attachment",
        "giftType": "donation",
        "confidenceScore": 0.91,
        "companyName": None,
    }

    NormalizationService().normalize_raw_object(db_session, raw_object, payload)
    db_session.commit()

    record = db_session.query(StagingGift).filter(StagingGift.raw_object_id == raw_object.id).one()
    assert record.source_system == "gmail"
    assert record.primary_email == "jane@example.org"
    assert str(record.amount) == "125.00"
    assert record.campaign_name == "Spring Appeal"
