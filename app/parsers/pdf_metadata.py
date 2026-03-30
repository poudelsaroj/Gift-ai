"""PDF metadata parser stub."""

from typing import Any

from app.parsers.base import BaseParser


class PdfMetadataParser(BaseParser):
    """Placeholder parser for PDF metadata extraction."""

    def extract_metadata(self, payload: Any) -> dict[str, Any]:
        if isinstance(payload, dict):
            return {
                "page_count": payload.get("page_count"),
                "text_preview": payload.get("text_preview"),
            }
        return {}

