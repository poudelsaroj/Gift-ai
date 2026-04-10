"""Deterministic parsing for known donation export spreadsheets."""

from __future__ import annotations

import csv
import io
import json
import re
from typing import Any

from app.models.source_config import SourceConfig


class StructuredTabularImportService:
    """Parse known donation-export schemas without relying on an LLM."""

    _SUPPORTED_EXTENSIONS = {".csv", ".tsv"}
    _REQUIRED_COLUMNS = {
        "source",
        "name",
        "email",
        "donation_amount",
        "currency",
        "payment_method",
        "transaction_id",
        "donation_date",
        "campaign_name",
        "fund_designation",
        "metadata",
    }

    def extract(
        self,
        *,
        content: bytes,
        filename: str,
        source: SourceConfig,
    ) -> dict[str, Any] | None:
        """Return canonical gift rows when the upload matches a known schema."""
        extension = self._extension(filename)
        if extension not in self._SUPPORTED_EXTENSIONS:
            return None
        text = content.decode("utf-8-sig")
        delimiter = "\t" if extension == ".tsv" else self._sniff_delimiter(text)
        reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
        fieldnames = {self._normalized_header(name) for name in reader.fieldnames or [] if name}
        if not self._REQUIRED_COLUMNS.issubset(fieldnames):
            return None

        gifts: list[dict[str, Any]] = []
        channels: set[str] = set()
        for row_number, row in enumerate(reader, start=1):
            row = self._repair_row(row)
            normalized = {self._normalized_header(key): self._clean(value) for key, value in row.items() if key}
            if self._is_blank_row(normalized):
                continue
            channel = normalized.get("source")
            if channel:
                channels.add(channel)
            transaction_id = normalized.get("transaction_id") or f"row-{row_number}"
            donor_type = normalized.get("donor_type")
            recurring = self._to_bool(normalized.get("is_recurring"))
            gift = {
                "recordType": "gift",
                "sourceRecordId": transaction_id,
                "sourceParentId": None,
                "giftId": transaction_id,
                "sourceFileId": filename,
                "primaryName": normalized.get("name"),
                "primaryEmail": normalized.get("email"),
                "donorName": normalized.get("name"),
                "donorEmail": normalized.get("email"),
                "companyName": normalized.get("name") if donor_type == "organization" else None,
                "amount": normalized.get("donation_amount"),
                "currency": normalized.get("currency") or "USD",
                "recordDate": normalized.get("donation_date"),
                "giftDate": normalized.get("donation_date"),
                "paymentType": normalized.get("payment_method"),
                "giftType": "recurring_donation" if recurring else "donation",
                "campaignId": normalized.get("campaign_name"),
                "campaignName": normalized.get("campaign_name"),
                "relatedEntityId": normalized.get("fund_designation"),
                "relatedEntityName": normalized.get("fund_designation") or channel,
                "receiptNumber": transaction_id,
                "memo": normalized.get("message") or normalized.get("reason"),
                "confidenceScore": 0.99,
                "sourceMedium": channel,
                "sourceFilename": filename,
                "sourceAttachmentId": None,
                "messageId": None,
                "extraMetadata": {
                    "donor_type": donor_type,
                    "is_recurring": recurring,
                    "frequency": normalized.get("frequency"),
                    "reason": normalized.get("reason"),
                    "fund_designation": normalized.get("fund_designation"),
                    "country": normalized.get("country"),
                    "city": normalized.get("city"),
                    "phone": normalized.get("phone"),
                    "tax_exempt": self._to_bool(normalized.get("tax_exempt")),
                    "receipt_sent": self._to_bool(normalized.get("receipt_sent")),
                    "source": channel,
                    "original_metadata": self._parse_json(normalized.get("metadata")),
                },
            }
            gifts.append(gift)

        return {
            "is_gift_file": True,
            "summary": (
                f"Recognized structured donation export for {source.source_name}: "
                f"{len(gifts)} gifts across {max(len(channels), 1)} channels."
            ),
            "gifts": gifts,
        }

    def _extension(self, filename: str) -> str:
        lowered = (filename or "").lower()
        if "." not in lowered:
            return ""
        return lowered[lowered.rfind(".") :]

    def _sniff_delimiter(self, text: str) -> str:
        try:
            return csv.Sniffer().sniff(text[:2048], delimiters=",;\t").delimiter
        except csv.Error:
            return ","

    def _normalized_header(self, value: str) -> str:
        return value.strip().lower().replace(" ", "_")

    def _clean(self, value: Any) -> str | None:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _is_blank_row(self, row: dict[str, str | None]) -> bool:
        return all(value in (None, "") for value in row.values())

    def _repair_row(self, row: dict[str | None, Any]) -> dict[str | None, Any]:
        repaired = dict(row)
        overflow = repaired.pop(None, None)
        if overflow:
            extras = [str(part).strip() for part in overflow if part not in (None, "")]
            if extras:
                existing = str(repaired.get("metadata") or "").strip()
                repaired["metadata"] = ",".join([part for part in [existing, *extras] if part])
        return repaired

    def _to_bool(self, value: str | None) -> bool | None:
        if value is None:
            return None
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
        return None

    def _parse_json(self, value: str | None) -> dict[str, Any] | None:
        if not value:
            return None
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            repaired = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', value)
            try:
                parsed = json.loads(repaired)
            except json.JSONDecodeError:
                return {"raw": value}
        return parsed if isinstance(parsed, dict) else {"value": parsed}
