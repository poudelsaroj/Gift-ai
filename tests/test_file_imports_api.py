"""Generic file import API tests."""

from sqlalchemy import select

from app.models.raw_object import RawObject
from app.models.staging_gift import StagingGift


def source_payload() -> dict:
    return {
        "source_name": "Manual CSV Source",
        "source_system": "csv",
        "acquisition_mode": "file_upload",
        "auth_type": "manual",
        "enabled": True,
        "config_json": {},
    }


def test_import_canonical_file_creates_raw_and_canonical_records(client, db_session, monkeypatch) -> None:
    created = client.post("/api/v1/sources", json=source_payload()).json()

    monkeypatch.setattr(
        "app.api.routes.file_imports.import_service.extract",
        lambda **kwargs: {
            "is_gift_file": True,
            "summary": "Found one gift row.",
            "gifts": [
                {
                    "recordType": "gift",
                    "sourceRecordId": "row-1",
                    "sourceParentId": None,
                    "giftId": "row-1",
                    "sourceFileId": "gifts.xlsx",
                    "primaryName": "Ava Carter",
                    "primaryEmail": "ava@example.org",
                    "donorName": "Ava Carter",
                    "donorEmail": "ava@example.org",
                    "companyName": None,
                    "amount": "1250.00",
                    "currency": "USD",
                    "recordDate": "2026-04-07",
                    "giftDate": "2026-04-07",
                    "paymentType": "ach",
                    "giftType": "donation",
                    "campaignId": None,
                    "campaignName": "Spring Drive",
                    "relatedEntityId": None,
                    "relatedEntityName": "uploaded_file",
                    "receiptNumber": "rcpt-1",
                    "memo": "Imported from spreadsheet",
                    "confidenceScore": 0.93,
                    "sourceMedium": "uploaded_file",
                    "sourceFilename": "gifts.xlsx",
                    "sourceAttachmentId": None,
                    "messageId": None,
                }
            ],
        },
    )

    response = client.post(
        f"/api/v1/files/sources/{created['id']}/imports/canonical",
        files={
            "file": (
                "gifts.xlsx",
                b"fake-xlsx-content",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["records_imported_count"] == 2

    raw_objects = list(
        db_session.scalars(select(RawObject).where(RawObject.source_id == created["id"]).order_by(RawObject.id))
    )
    assert [item.external_object_type for item in raw_objects] == ["uploaded_file", "gift_extract"]

    record = db_session.scalar(select(StagingGift).where(StagingGift.source_system == "csv"))
    assert record is not None
    assert record.primary_email == "ava@example.org"
    assert str(record.amount) == "1250.00"
    assert record.source_file_id == "gifts.xlsx"


def test_import_canonical_file_assigns_row_ids_for_multiple_gifts(client, db_session, monkeypatch) -> None:
    created = client.post("/api/v1/sources", json=source_payload()).json()

    monkeypatch.setattr(
        "app.api.routes.file_imports.import_service.extract",
        lambda **kwargs: {
            "is_gift_file": True,
            "summary": "Found two gift rows.",
            "gifts": [
                {
                    "primaryName": "Olivia Martinez",
                    "primaryEmail": "olivia@example.org",
                    "donorName": "Olivia Martinez",
                    "donorEmail": "olivia@example.org",
                    "amount": "8500.00",
                    "currency": "USD",
                    "recordDate": "2026-04-07",
                    "giftDate": "2026-04-07",
                    "giftType": "donation",
                    "paymentType": "ach",
                    "campaignName": "Community Fund",
                    "sourceMedium": "uploaded_file",
                    "sourceFilename": "gifts.csv",
                },
                {
                    "primaryName": "Liam Carter",
                    "primaryEmail": "liam@example.org",
                    "donorName": "Liam Carter",
                    "donorEmail": "liam@example.org",
                    "amount": "1200.00",
                    "currency": "USD",
                    "recordDate": "2026-04-07",
                    "giftDate": "2026-04-07",
                    "giftType": "donation",
                    "paymentType": "card",
                    "campaignName": "Community Fund",
                    "sourceMedium": "uploaded_file",
                    "sourceFilename": "gifts.csv",
                },
            ],
        },
    )

    response = client.post(
        f"/api/v1/files/sources/{created['id']}/imports/canonical",
        files={"file": ("gifts.csv", b"name,amount\nolivia,8500", "text/csv")},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["records_imported_count"] == 3

    records = list(
        db_session.scalars(
            select(StagingGift)
            .where(StagingGift.source_system == "csv")
            .order_by(StagingGift.id)
        )
    )
    assert len(records) == 2
    assert [record.gift_id for record in records] == ["1", "2"]
    assert [record.source_record_id for record in records] == ["1", "2"]
    assert [record.primary_email for record in records] == ["olivia@example.org", "liam@example.org"]


def test_import_canonical_file_rejects_unsupported_extension(client) -> None:
    created = client.post("/api/v1/sources", json=source_payload()).json()

    response = client.post(
        f"/api/v1/files/sources/{created['id']}/imports/canonical",
        files={"file": ("gifts.xls", b"legacy", "application/vnd.ms-excel")},
    )

    assert response.status_code == 422
    assert "CSV, TSV, or XLSX" in response.json()["detail"]
