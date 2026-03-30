"""OneCause connector tests."""

import json
from pathlib import Path

import httpx

from app.connectors.base.types import FetchRequest
from app.connectors.onecause.connector import OneCauseConnector


def load_fixture(name: str) -> dict:
    return json.loads((Path(__file__).parent / "fixtures" / name).read_text(encoding="utf-8"))


def base_config() -> dict:
    return {
        "api_base_url": "https://api.onecause.example",
        "api_key": "secret-key",
        "organization_id": "org-123",
        "enabled_object_types": ["paid_activities", "supporters"],
        "list_key_overrides": {
            "paid_activities": "paidActivities",
            "supporters": "supporters",
        },
    }


def handler(request: httpx.Request) -> httpx.Response:
    if request.url.path.endswith("/paid-activities"):
        return httpx.Response(200, json=load_fixture("onecause_paid_activities.json"))
    if request.url.path.endswith("/supporters"):
        return httpx.Response(200, json=load_fixture("onecause_supporters.json"))
    if request.url.path.endswith("/events"):
        return httpx.Response(200, json={"events": [{"id": 5001}], "pagination": {"page": 1, "total_pages": 1}})
    return httpx.Response(404, json={"detail": "not found"})


def test_onecause_test_connection(monkeypatch) -> None:
    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.client = original_client(transport=transport)

        def __enter__(self):
            return self.client

        def __exit__(self, exc_type, exc, tb):
            self.client.close()

    monkeypatch.setattr("app.connectors.onecause.client.httpx.Client", MockClient)
    connector = OneCauseConnector(base_config())
    response = connector.test_connection()
    assert response["ok"] is True
    assert "/organizations/org-123/events" in response["test_endpoint"]


def test_onecause_fetch(monkeypatch) -> None:
    transport = httpx.MockTransport(handler)
    original_client = httpx.Client

    class MockClient:
        def __init__(self, *args, **kwargs):
            self.client = original_client(transport=transport)

        def __enter__(self):
            return self.client

        def __exit__(self, exc_type, exc, tb):
            self.client.close()

    monkeypatch.setattr("app.connectors.onecause.client.httpx.Client", MockClient)
    connector = OneCauseConnector(base_config())
    result = connector.fetch(FetchRequest(run_type="incremental", trigger_type="manual"))
    assert len(result.items) == 3
    assert result.items[0].external_object_id == "101"
    assert "paid_activities" in result.cursor_state
