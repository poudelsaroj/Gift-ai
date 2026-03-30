"""Email connector skeleton."""

from app.connectors.base.connector import BaseConnector
from app.connectors.base.types import FetchRequest, FetchResult


class EmailConnector(BaseConnector):
    """Skeleton connector for email-based ingestion."""

    source_system = "email"
    acquisition_mode = "email"

    def validate_config(self) -> None:
        required = {"mailbox", "auth_method"}
        missing = required - set(self.config)
        if missing:
            raise ValueError(f"Missing email config fields: {sorted(missing)}")

    def test_connection(self) -> dict:
        self.validate_config()
        return {"ok": True, "message": "Email connector skeleton validated."}

    def fetch(self, request: FetchRequest) -> FetchResult:
        return FetchResult(items=[], cursor_state=request.cursor_state, metadata={"mode": "skeleton"})

    def normalize_raw_metadata(self, payload):
        return {"attachment_count": len(payload.get("attachments", []))} if isinstance(payload, dict) else {}

    def extract_external_ids(self, payload):
        if isinstance(payload, dict):
            return {"external_object_id": payload.get("message_id"), "external_parent_id": None}
        return {"external_object_id": None, "external_parent_id": None}

    def list_supported_objects(self) -> list[str]:
        return ["email_message", "email_attachment"]

