"""Email metadata parser stub."""

from typing import Any

from app.parsers.base import BaseParser


class EmailMetadataParser(BaseParser):
    """Placeholder parser for email payload metadata extraction."""

    def extract_metadata(self, payload: Any) -> dict[str, Any]:
        if isinstance(payload, dict):
            return {
                "attachment_count": len(payload.get("attachments", [])),
                "subject": payload.get("subject"),
            }
        return {}

