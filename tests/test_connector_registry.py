"""Connector registry tests."""

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult
from app.connectors.registry import ConnectorRegistry


def test_registry_discovers_existing_connectors() -> None:
    source_systems = ConnectorRegistry.supported_source_systems()
    assert "onecause" in source_systems
    assert "everyorg" in source_systems
    assert "pledge" in source_systems


def test_registry_can_register_connector_explicitly() -> None:
    class ManualTestConnector(BaseConnector):
        source_system = "manual_test"
        acquisition_mode = "api"

        def validate_config(self) -> None:
            return None

        def test_connection(self) -> dict[str, bool]:
            return {"ok": True}

        def fetch(self, request: FetchRequest) -> FetchResult:
            return FetchResult(items=[], cursor_state=None)

        def normalize_raw_metadata(self, payload):
            return {}

        def extract_external_ids(self, payload):
            return {"external_object_id": None, "external_parent_id": None}

        def list_supported_objects(self) -> list[str]:
            return ["example"]

    ConnectorRegistry.register(ManualTestConnector)
    connector = ConnectorRegistry.create_connector("manual_test", {"enabled": True})
    assert isinstance(connector, ManualTestConnector)
