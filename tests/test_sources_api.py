"""Source API tests."""

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models.source_config import SourceConfig


def onecause_payload() -> dict:
    return {
        "source_name": "OneCause Primary",
        "source_system": "onecause",
        "acquisition_mode": "api",
        "auth_type": "api_key",
        "enabled": True,
        "config_json": {
            "api_base_url": "https://api.onecause.example",
            "api_key": "secret-key",
            "organization_id": "org-123",
            "enabled_object_types": ["paid_activities"],
        },
    }


def pledge_payload() -> dict:
    return {
        "source_name": "Pledge Donations",
        "source_system": "pledge",
        "acquisition_mode": "api",
        "auth_type": "bearer",
        "enabled": True,
        "config_json": {
            "api_base_url": "https://api.pledge.example",
            "api_key": "pledge-secret",
        },
    }


def test_create_source(client: TestClient) -> None:
    response = client.post("/api/v1/sources", json=onecause_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["source_name"] == "OneCause Primary"
    assert body["source_system"] == "onecause"


def test_create_source_uses_env_defaults(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("ONECAUSE_API_BASE_URL", "https://api.onecause.example")
    monkeypatch.setenv("ONECAUSE_API_KEY", "env-secret")
    monkeypatch.setenv("ONECAUSE_ORGANIZATION_ID", "env-org")

    payload = {
        "source_name": "OneCause Env Defaults",
        "source_system": "onecause",
        "acquisition_mode": "api",
        "auth_type": "api_key",
        "enabled": True,
        "config_json": {},
    }
    response = client.post("/api/v1/sources", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["config_json"]["api_base_url"] == "https://api.onecause.example"
    assert body["config_json"]["organization_id"] == "env-org"
    assert body["config_json"]["api_key"] == "***REDACTED***"


def test_create_source_access_token_defaults(client: TestClient, monkeypatch) -> None:
    monkeypatch.delenv("ONECAUSE_API_KEY", raising=False)
    monkeypatch.delenv("ONECAUSE_ORGANIZATION_ID", raising=False)
    monkeypatch.setenv("ONECAUSE_API_BASE_URL", "https://p2p.onecause.com")
    monkeypatch.setenv("ONECAUSE_CLIENT_ID", "client-123")
    monkeypatch.setenv("ONECAUSE_ACCESS_TOKEN", "portal-token")

    payload = {
        "source_name": "OneCause Portal Fallback",
        "source_system": "onecause",
        "acquisition_mode": "api",
        "auth_type": "access_token",
        "enabled": True,
        "config_json": {"auth_mode": "access_token"},
    }
    response = client.post("/api/v1/sources", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["config_json"]["auth_mode"] == "access_token"
    assert body["config_json"]["client_id"] == "client-123"
    assert body["config_json"]["auth_header_name"] == "x-access-token"



def test_update_source(client: TestClient) -> None:
    created = client.post("/api/v1/sources", json=onecause_payload()).json()
    response = client.patch(
        f"/api/v1/sources/{created['id']}",
        json={"source_name": "OneCause Updated", "enabled": False},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["source_name"] == "OneCause Updated"
    assert body["enabled"] is False


def test_create_pledge_source(client: TestClient) -> None:
    response = client.post("/api/v1/sources", json=pledge_payload())
    assert response.status_code == 201
    body = response.json()
    assert body["source_name"] == "Pledge Donations"
    assert body["source_system"] == "pledge"
    assert body["config_json"]["api_key"] == "***REDACTED***"


def test_create_pledge_source_uses_env_defaults(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("PLEDGE_API_BASE_URL", "https://api.pledge.example")
    monkeypatch.setenv("PLEDGE_API_KEY", "env-pledge-secret")

    payload = {
        "source_name": "Pledge Env Defaults",
        "source_system": "pledge",
        "acquisition_mode": "api",
        "auth_type": "bearer",
        "enabled": True,
        "config_json": {},
    }
    response = client.post("/api/v1/sources", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["config_json"]["api_base_url"] == "https://api.pledge.example"
    assert body["config_json"]["api_key"] == "***REDACTED***"


def test_trigger_source_returns_422_for_runtime_validation_error(
    client: TestClient,
    monkeypatch,
) -> None:
    created = client.post("/api/v1/sources", json=onecause_payload()).json()

    def raise_value_error(*args, **kwargs):
        raise ValueError("OpenAI Responses API request failed with status 403: forbidden")

    monkeypatch.setattr(
        "app.api.routes.sources.ingestion_service.execute",
        raise_value_error,
    )

    response = client.post(
        f"/api/v1/sources/{created['id']}/trigger",
        json={"run_type": "incremental", "trigger_type": "manual"},
    )

    assert response.status_code == 422
    assert "403" in response.json()["detail"]


def test_test_source_persists_runtime_config_updates(
    client: TestClient,
    db_session,
    monkeypatch,
) -> None:
    created = client.post("/api/v1/sources", json=onecause_payload()).json()

    class FakeConnector:
        def validate_config(self) -> None:
            return None

        def test_connection(self) -> dict:
            return {"ok": True, "status": "connected"}

        def runtime_config_updates(self) -> dict:
            return {"access_token": "new-runtime-token"}

    monkeypatch.setattr(
        "app.api.routes.sources.ConnectorRegistry.get_connector",
        lambda source_system, config: FakeConnector(),
    )

    response = client.post(f"/api/v1/sources/{created['id']}/test")

    assert response.status_code == 200
    source = db_session.scalar(select(SourceConfig).where(SourceConfig.id == created["id"]))
    assert source is not None
    assert source.config_json["access_token"] == "new-runtime-token"
