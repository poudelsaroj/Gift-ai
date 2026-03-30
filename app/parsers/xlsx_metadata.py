"""XLSX metadata parser stub."""

from typing import Any

from app.parsers.base import BaseParser


class XlsxMetadataParser(BaseParser):
    """Placeholder parser for XLSX metadata extraction."""

    def extract_metadata(self, payload: Any) -> dict[str, Any]:
        if isinstance(payload, dict):
            return {
                "sheet_count": payload.get("sheet_count"),
                "column_names": payload.get("column_names", []),
            }
        return {}

