"""Ingestion service architecture tests."""

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult, RawFetchItem
from app.models.raw_object import RawObject
from app.models.source_config import SourceConfig
from app.services.ingestion_service import IngestionService
from app.services.raw_item_ingestion_service import RawItemIngestionService
from app.storage.filesystem import FilesystemStorage


class FakeConnector(BaseConnector):
    source_system = "fake"
    acquisition_mode = "api"

    def validate_config(self) -> None:
        return None

    def test_connection(self) -> dict[str, bool]:
        return {"ok": True}

    def fetch(self, request: FetchRequest) -> FetchResult:
        return FetchResult(
            items=[
                RawFetchItem(
                    object_type="donation",
                    external_object_id="gift-1",
                    payload={"id": "gift-1", "email": "donor@example.org", "amount": 25},
                )
            ],
            cursor_state={"donation": {"last_end_time": "2026-04-03T00:00:00+00:00"}},
            metadata={"source": "fake"},
        )

    def normalize_raw_metadata(self, payload):
        return {}

    def extract_external_ids(self, payload):
        return {"external_object_id": "gift-1", "external_parent_id": None}

    def list_supported_objects(self) -> list[str]:
        return ["donation"]


class FakeConnectorRegistry:
    @staticmethod
    def create_connector(source_system: str, config: dict) -> BaseConnector:
        assert source_system == "fake"
        return FakeConnector(config)


def test_ingestion_service_executes_through_injected_dependencies(db_session, tmp_path) -> None:
    source = SourceConfig(
        source_name="Fake Source",
        source_system="fake",
        acquisition_mode="api",
        auth_type="none",
        enabled=True,
        config_json={"enabled": True},
    )
    db_session.add(source)
    db_session.commit()
    db_session.refresh(source)

    service = IngestionService(
        connector_registry=FakeConnectorRegistry,
        raw_item_ingestion_service=RawItemIngestionService(
            storage=FilesystemStorage(str(tmp_path / "raw-storage"))
        ),
    )

    run = service.execute(
        db_session,
        source,
        run_type="incremental",
        trigger_type="manual",
    )

    raw_objects = db_session.query(RawObject).all()
    assert run.status == "completed"
    assert run.records_fetched_count == 1
    assert run.metadata_json == {"source": "fake"}
    assert len(raw_objects) == 1
    assert raw_objects[0].source_system == "fake"
