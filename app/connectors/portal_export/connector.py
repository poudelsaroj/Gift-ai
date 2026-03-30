"""Portal export connector skeleton."""

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult


class PortalExportConnector(BaseConnector):
    """Skeleton connector for portal-export ingestion."""

    source_system = "portal_export"
    acquisition_mode = "portal_export"

    def validate_config(self) -> None:
        if "export_pattern" not in self.config:
            raise ValueError("Missing required portal export config field: export_pattern")

    def test_connection(self) -> dict:
        self.validate_config()
        return {"ok": True, "message": "Portal-export connector skeleton validated."}

    def fetch(self, request: FetchRequest) -> FetchResult:
        return FetchResult(items=[], cursor_state=request.cursor_state, metadata={"mode": "skeleton"})

    def normalize_raw_metadata(self, payload):
        return {"preview": str(payload)[:100]}

    def extract_external_ids(self, payload):
        if isinstance(payload, dict):
            return {"external_object_id": payload.get("export_id"), "external_parent_id": None}
        return {"external_object_id": None, "external_parent_id": None}

    def list_supported_objects(self) -> list[str]:
        return ["export_file"]

