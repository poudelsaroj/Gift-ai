"""Gmail source API tests."""

from fastapi.testclient import TestClient


def gmail_payload() -> dict:
    return {
        "source_name": "Gift Mailbox",
        "source_system": "gmail",
        "acquisition_mode": "email",
        "auth_type": "oauth",
        "enabled": True,
        "config_json": {},
    }


def test_create_gmail_source_uses_env_defaults(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("GMAIL_ACCESS_TOKEN", "gmail-access-token")
    monkeypatch.setenv("GMAIL_QUERY", "label:gifts newer_than:30d")

    response = client.post("/api/v1/sources", json=gmail_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["source_system"] == "gmail"
    assert body["config_json"]["query"] == "label:gifts newer_than:30d"
    assert body["config_json"]["access_token"] == "***REDACTED***"
