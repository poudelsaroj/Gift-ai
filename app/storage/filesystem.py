"""Filesystem raw storage implementation."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.storage.base import BaseStorage


class FilesystemStorage(BaseStorage):
    """Store raw payloads on the local filesystem."""

    def __init__(self, root: str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_json_payload(
        self,
        *,
        source_system: str,
        run_id: int,
        object_type: str,
        object_id: str | None,
        payload: dict[str, Any] | list[Any],
        fetched_at: datetime,
    ) -> str:
        path = self.build_storage_path(
            source_system=source_system,
            fetched_at=fetched_at,
            run_id=run_id,
            object_type=object_type,
            object_id=object_id,
            extension=".json",
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return str(path)

    def save_binary_file(
        self,
        *,
        source_system: str,
        run_id: int,
        object_type: str,
        object_id: str | None,
        filename: str,
        content: bytes,
        fetched_at: datetime,
    ) -> str:
        suffix = Path(filename).suffix or ".bin"
        path = self.build_storage_path(
            source_system=source_system,
            fetched_at=fetched_at,
            run_id=run_id,
            object_type=object_type,
            object_id=object_id,
            extension=suffix,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path)

    def get_payload(self, path: str) -> dict[str, Any] | str:
        payload_path = Path(path)
        if payload_path.suffix == ".json":
            return json.loads(payload_path.read_text(encoding="utf-8"))
        return payload_path.read_text(encoding="utf-8")

    def build_storage_path(
        self,
        *,
        source_system: str,
        fetched_at: datetime,
        run_id: int,
        object_type: str,
        object_id: str | None,
        extension: str,
    ) -> Path:
        safe_object_id = object_id or "unknown"
        date_path = fetched_at.strftime("%Y/%m/%d")
        filename = f"{safe_object_id}{extension}"
        return self.root / source_system / date_path / f"run_{run_id}" / object_type / filename

