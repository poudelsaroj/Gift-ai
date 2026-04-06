"""Shared email ingestion dataclasses."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class ParsedAttachment:
    """Parsed attachment metadata and content."""

    attachment_id: str
    part_id: str | None
    filename: str
    mime_type: str
    size: int | None
    data: bytes


@dataclass(slots=True)
class ParsedEmail:
    """Normalized email payload extracted from provider-specific APIs."""

    message_id: str
    thread_id: str | None
    history_id: str | None
    internal_date: datetime | None
    subject: str | None
    from_email: str | None
    from_name: str | None
    to_email: str | None
    labels: list[str]
    snippet: str | None
    body_text: str | None
    body_html: str | None
    attachments: list[ParsedAttachment]
    raw_payload: dict[str, Any]
