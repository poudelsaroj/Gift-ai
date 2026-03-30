"""Shared-folder connector skeleton."""

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult


class SharedFolderConnector(BaseConnector):
    """Skeleton connector for shared-folder ingestion."""

    source_system = "shared_folder"
    acquisition_mode = "shared_folder"

    def validate_config(self) -> None:
        if "root_path" not in self.config:
            raise ValueError("Missing required shared folder config field: root_path")

    def test_connection(self) -> dict:
        self.validate_config()
        return {"ok": True, "message": "Shared-folder connector skeleton validated."}

    def fetch(self, request: FetchRequest) -> FetchResult:
        return FetchResult(items=[], cursor_state=request.cursor_state, metadata={"mode": "skeleton"})

    def normalize_raw_metadata(self, payload):
        if isinstance(payload, dict):
            return {"keys": sorted(payload.keys())}
        return {}

    def extract_external_ids(self, payload):
        if isinstance(payload, dict):
            return {"external_object_id": payload.get("path"), "external_parent_id": payload.get("folder")}
        return {"external_object_id": None, "external_parent_id": None}

    def list_supported_objects(self) -> list[str]:
        return ["file"]

