"""Scheduler API tests."""

from fastapi.testclient import TestClient


def test_run_due_sources_supports_force_flag(client: TestClient, monkeypatch) -> None:
    called: dict[str, bool] = {}

    def fake_run_due_sources(*, force: bool = False) -> int:
        called["force"] = force
        return 1

    monkeypatch.setattr(
        "app.api.routes.scheduler.scheduler_service.run_due_sources",
        fake_run_due_sources,
    )

    response = client.post("/api/v1/scheduler/run-due?force=true")

    assert response.status_code == 200
    assert response.json() == {"started": 1, "force": True}
    assert called["force"] is True


def test_run_due_sources_returns_502_on_failure(client: TestClient, monkeypatch) -> None:
    def fake_run_due_sources(*, force: bool = False) -> int:
        raise ValueError("gmail auth failed")

    monkeypatch.setattr(
        "app.api.routes.scheduler.scheduler_service.run_due_sources",
        fake_run_due_sources,
    )

    response = client.post("/api/v1/scheduler/run-due?force=true")

    assert response.status_code == 502
    assert response.json() == {"detail": "gmail auth failed"}
