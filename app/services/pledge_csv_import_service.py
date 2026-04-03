"""Parse Pledge donation CSV exports into raw fetch items."""

from __future__ import annotations

import csv
import io
import re
from datetime import UTC, datetime

from app.connectors.base.types import RawFetchItem
from app.models.source_config import SourceConfig


class PledgeCSVImportService:
    """Convert Pledge donation CSV exports into normalized raw items."""

    _EMPTY_VALUES = {"", "n/a", "na", "none", "null", "-"}

    def parse_csv(
        self,
        content: bytes,
        *,
        filename: str | None,
        source: SourceConfig,
    ) -> list[RawFetchItem]:
        """Parse a Pledge donation export into raw fetch items."""
        text = self._decode_bytes(content)
        reader = csv.DictReader(io.StringIO(text))
        items: list[RawFetchItem] = []
        for row_number, raw_row in enumerate(reader, start=2):
            cleaned = self._clean_row(raw_row)
            if not cleaned:
                continue
            if self._is_processing_fee_row(cleaned):
                continue
            payload = self._build_payload(cleaned, source=source)
            donation_id = payload.get("id")
            fundraiser = payload.get("fundraiser") if isinstance(payload.get("fundraiser"), dict) else {}
            fundraiser_id = fundraiser.get("id")
            items.append(
                RawFetchItem(
                    object_type="donations",
                    external_object_id=str(donation_id) if donation_id else None,
                    external_parent_id=str(fundraiser_id) if fundraiser_id else None,
                    payload=payload,
                    event_timestamp=self._parse_datetime(payload.get("created_at")),
                    content_type="text/csv",
                    source_channel="portal_export",
                    original_filename=filename,
                    metadata={"import_kind": "pledge_donations_csv", "row_number": row_number},
                )
            )
        return items

    def _decode_bytes(self, content: bytes) -> str:
        for encoding in ("utf-8-sig", "utf-8", "cp1252"):
            try:
                return content.decode(encoding)
            except UnicodeDecodeError:
                continue
        return content.decode("utf-8", errors="replace")

    def _clean_row(self, row: dict[str, str | None]) -> dict[str, str]:
        cleaned: dict[str, str] = {}
        for key, value in row.items():
            if key is None:
                continue
            normalized_key = self._normalize_key(key)
            if not normalized_key:
                continue
            cleaned[normalized_key] = str(value or "").strip()
        if not any(value for value in cleaned.values()):
            return {}
        return cleaned

    def _build_payload(self, row: dict[str, str], *, source: SourceConfig) -> dict[str, object]:
        donor_email = self._clean_value(row.get("donor_email"))
        fundraiser_name = self._clean_value(row.get("fundraiser_name"))
        fundraiser_url = self._clean_value(row.get("fundraiser_url"))
        campaign_id = self._clean_value(row.get("campaign_id"))
        source_name = self._clean_value(row.get("source")) or source.source_name
        donor_name = " ".join(
            part
            for part in [
                self._clean_value(row.get("donor_first_name")) or "",
                self._clean_value(row.get("donor_last_name")) or "",
            ]
            if part
        ) or None

        payload: dict[str, object] = {
            "id": self._clean_value(row.get("id")),
            "created_at": self._normalize_date(row.get("date")),
            "amount": self._normalize_amount(row.get("gross_amount")),
            "currency": self._infer_currency(row.get("original_amount")) or "USD",
            "payment_method": self._clean_value(row.get("payment_method")),
            "reference": self._clean_value(row.get("payout_id")) or self._clean_value(row.get("donor_id")),
            "message": self._clean_value(row.get("project_designation")) or self._clean_value(row.get("custom_response")),
            "donor": {
                "name": donor_name or row.get("source"),
                "email": donor_email,
                "first_name": self._clean_value(row.get("donor_first_name")),
                "last_name": self._clean_value(row.get("donor_last_name")),
            },
            "organization": {
                "name": source.source_name,
                "profile_url": None,
                "ngo_id": None,
            },
            "fundraiser": {
                "id": campaign_id or fundraiser_name or None,
                "title": fundraiser_name or source_name,
                "name": fundraiser_name or source_name,
                "url": fundraiser_url or None,
            },
        }
        return payload

    def _clean_value(self, value: str | None) -> str | None:
        if value is None:
            return None
        text = value.strip()
        if text.lower() in self._EMPTY_VALUES:
            return None
        return text

    def _normalize_key(self, value: str) -> str:
        compact = " ".join(value.replace("\n", " ").split())
        return re.sub(r"[^a-z0-9]+", "_", compact.strip().lower()).strip("_")

    def _normalize_amount(self, value: str | None) -> str | None:
        if not value:
            return None
        normalized = re.sub(r"[^0-9.\-]", "", value)
        if not normalized:
            return None
        if normalized.count(".") > 1:
            head, *tail = normalized.split(".")
            normalized = f"{head}.{''.join(tail)}"
        return normalized

    def _infer_currency(self, value: str | None) -> str | None:
        if not value:
            return None
        match = re.search(r"\b([A-Z]{3})\b", value)
        return match.group(1) if match else None

    def _normalize_date(self, value: str | None) -> str:
        parsed = self._parse_datetime(value)
        if parsed is None:
            return datetime.now(tz=UTC).isoformat()
        return parsed.isoformat().replace("+00:00", "Z")

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if not value:
            return None
        text = " ".join(value.split())
        for fmt in ("%m/%d/%y %I:%M %p", "%m/%d/%Y %I:%M %p", "%m/%d/%y %H:%M", "%m/%d/%Y %H:%M"):
            try:
                return datetime.strptime(text, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        return None

    def _is_processing_fee_row(self, row: dict[str, str]) -> bool:
        donor_email = (self._clean_value(row.get("donor_email")) or "").lower()
        donor_first = (self._clean_value(row.get("donor_first_name")) or "").lower()
        donor_last = (self._clean_value(row.get("donor_last_name")) or "").lower()
        source_name = (self._clean_value(row.get("source")) or "").lower()
        gross_amount = self._normalize_amount(row.get("gross_amount")) or ""
        return (
            donor_email == "processing.fee@pledge.to"
            or (donor_first == "pledgeling" and donor_last == "accounting")
            or source_name == "pledgeling technologies"
            or gross_amount.startswith("-")
        )
