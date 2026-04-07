"""Manual CSV/XLSX upload connector."""

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult


class CsvConnector(BaseConnector):
    """Connector for manual spreadsheet uploads normalized into canonical gifts."""

    source_system = "csv"
    acquisition_mode = "file_upload"

    def validate_config(self) -> None:
        """Manual uploads do not require external configuration."""

    def test_connection(self) -> dict:
        return {"ok": True, "message": "CSV upload source is ready for manual imports."}

    def fetch(self, request: FetchRequest) -> FetchResult:
        return FetchResult(items=[], cursor_state=request.cursor_state, metadata={"mode": "manual_upload"})

    def normalize_raw_metadata(self, payload):
        if isinstance(payload, dict):
            return {"filename": payload.get("filename"), "size": payload.get("size")}
        return {}

    def extract_external_ids(self, payload):
        if isinstance(payload, dict):
            return {"external_object_id": payload.get("sourceRecordId"), "external_parent_id": payload.get("sourceParentId")}
        return {"external_object_id": None, "external_parent_id": None}

    def list_supported_objects(self) -> list[str]:
        return ["uploaded_file", "gift_extract"]
