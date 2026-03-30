"""CSV metadata parser stub."""

from typing import Any

from app.parsers.base import BaseParser


class CsvMetadataParser(BaseParser):
    """Placeholder parser for CSV metadata extraction."""

    def extract_metadata(self, payload: Any) -> dict[str, Any]:
        if isinstance(payload, dict):
            return {
                "row_count": payload.get("row_count"),
                "column_names": payload.get("column_names", []),
            }
        return {}

