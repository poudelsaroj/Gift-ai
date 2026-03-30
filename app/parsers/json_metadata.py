"""JSON metadata parser."""

from typing import Any

from app.parsers.base import BaseParser


class JsonMetadataParser(BaseParser):
    """Metadata-only parser for JSON payloads."""

    def extract_metadata(self, payload: Any) -> dict[str, Any]:
        if isinstance(payload, dict):
            return {"top_level_keys": sorted(payload.keys())}
        if isinstance(payload, list):
            return {"row_count": len(payload)}
        return {"preview": str(payload)[:200]}

