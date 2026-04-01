"""Every.org source and webhook tests."""

from decimal import Decimal

from fastapi.testclient import TestClient
import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun
from app.models.raw_object import RawObject
from app.models.staging_gift import StagingGift


def everyorg_source_payload() -> dict:
    return {
        "source_name": "Every.org Donations",
        "source_system": "everyorg",
        "acquisition_mode": "webhook",
        "auth_type": "webhook",
        "enabled": True,
        "config_json": {
            "webhook_token": "everyorg-secret",
            "webhook_kind": "nonprofit",
            "nonprofit_slug": "demo-org",
        },
    }


def everyorg_webhook_payload() -> dict:
    return {
        "chargeId": "charge-123",
        "partnerDonationId": "partner-789",
        "firstName": "Jane",
        "lastName": "Doe",
        "email": "jane@example.org",
        "toNonprofit": {
            "slug": "demo-org",
            "ein": "123456789",
            "name": "Demo Org",
        },
        "amount": "100.00",
        "netAmount": "96.50",
        "currency": "USD",
        "frequency": "One-time",
        "donationDate": "2026-03-30T10:00:00Z",
        "designation": "Scholarship Fund",
        "paymentMethod": "card",
        "fromFundraiser": {
            "id": "fundraiser-1",
            "title": "Spring Drive",
            "slug": "spring-drive",
        },
    }


def test_create_everyorg_source(client: TestClient) -> None:
    response = client.post("/api/v1/sources", json=everyorg_source_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["source_system"] == "everyorg"
    assert body["config_json"]["webhook_token"] == "***REDACTED***"


def test_receive_everyorg_webhook(client: TestClient, db_session: Session) -> None:
    created = client.post("/api/v1/sources", json=everyorg_source_payload()).json()

    response = client.post(
        f"/api/v1/webhooks/everyorg/{created['id']}?token=everyorg-secret",
        json=everyorg_webhook_payload(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["duplicate_status"] == "unique"

    run = db_session.scalar(select(IngestionRun).where(IngestionRun.id == body["ingestion_run_id"]))
    raw_object = db_session.scalar(select(RawObject).where(RawObject.id == body["raw_object_id"]))
    gift = db_session.scalar(select(StagingGift).where(StagingGift.raw_object_id == body["raw_object_id"]))

    assert run is not None
    assert run.status == "completed"
    assert run.records_fetched_count == 1
    assert raw_object is not None
    assert raw_object.external_object_id == "charge-123"
    assert raw_object.external_parent_id == "fundraiser-1"
    assert gift is not None
    assert gift.gift_id == "charge-123"
    assert gift.donor_name == "Jane Doe"
    assert gift.amount == Decimal("100.00")
    assert gift.currency == "USD"
    assert gift.source_file_id == "demo-org"


def test_receive_everyorg_webhook_rejects_invalid_token(client: TestClient) -> None:
    created = client.post("/api/v1/sources", json=everyorg_source_payload()).json()

    response = client.post(
        f"/api/v1/webhooks/everyorg/{created['id']}?token=wrong-token",
        json=everyorg_webhook_payload(),
    )

    assert response.status_code == 403


def test_everyorg_source_cannot_be_triggered_manually(client: TestClient) -> None:
    created = client.post("/api/v1/sources", json=everyorg_source_payload()).json()

    response = client.post(
        f"/api/v1/sources/{created['id']}/trigger",
        json={"run_type": "incremental", "trigger_type": "manual"},
    )

    assert response.status_code == 400
    assert "webhook-only" in response.json()["detail"]


def test_everyorg_public_profile_uses_env_public_key(client: TestClient, monkeypatch) -> None:
    transport = httpx.MockTransport(
        lambda request: httpx.Response(
            200,
            json={
                "data": {
                    "nonprofit": {
                        "id": "np-1",
                        "name": "Demo Org",
                        "primarySlug": "demo-org",
                        "ein": "123456789",
                        "donationsEnabled": True,
                        "locationAddress": "Chicago, IL",
                        "websiteUrl": "https://demo.example",
                        "profileUrl": "https://www.every.org/demo-org",
                        "description": "Demo nonprofit profile",
                    }
                }
            },
        )
    )
    original_client = httpx.Client

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.client = original_client(transport=transport)

        def __enter__(self):
            return self.client

        def __exit__(self, exc_type, exc, tb):
            self.client.close()

    monkeypatch.setenv("EVERYORG_PUBLIC_KEY", "pk_test_demo")
    monkeypatch.setattr("app.connectors.everyorg.client.httpx.Client", MockClient)

    created = client.post("/api/v1/sources", json=everyorg_source_payload()).json()
    response = client.get(f"/api/v1/everyorg/sources/{created['id']}/nonprofit")

    assert response.status_code == 200
    body = response.json()
    assert body["source_id"] == created["id"]
    assert body["nonprofit"]["name"] == "Demo Org"
    assert body["nonprofit"]["primarySlug"] == "demo-org"
