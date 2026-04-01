"""Parse Every.org dashboard donation CSV exports into raw fetch items."""

from __future__ import annotations

import csv
import hashlib
import io
import re
from datetime import UTC, datetime
from typing import Any

from app.connectors.base.types import RawFetchItem
from app.models.source_config import SourceConfig


class EveryOrgDashboardImportService:
    """Convert Every.org dashboard CSV exports into normalized raw items."""

    _EMPTY_VALUES = {"", "n/a", "na", "none", "null", "-"}

    def parse_csv(
        self,
        content: bytes,
        *,
        filename: str | None,
        source: SourceConfig,
    ) -> list[RawFetchItem]:
        """Parse a dashboard CSV export into raw fetch items."""
        text = self._decode_bytes(content)
        reader = csv.DictReader(io.StringIO(text))
        items: list[RawFetchItem] = []
        for row_number, raw_row in enumerate(reader, start=2):
            cleaned_row = self._clean_row(raw_row)
            if not cleaned_row:
                continue
            payload = self._build_payload(cleaned_row, row_number=row_number, source=source)
            fundraiser = payload.get("fromFundraiser")
            fundraiser_id = fundraiser.get("id") if isinstance(fundraiser, dict) else None
            items.append(
                RawFetchItem(
                    object_type="donation_export",
                    external_object_id=(
                        str(payload.get("chargeId")) if payload.get("chargeId") else None
                    ),
                    external_parent_id=str(fundraiser_id) if fundraiser_id else None,
                    payload=payload,
                    event_timestamp=self._parse_datetime(payload.get("donationDate")),
                    content_type="text/csv",
                    source_channel="portal_export",
                    original_filename=filename,
                    metadata={
                        "import_kind": "everyorg_dashboard_csv",
                        "row_number": row_number,
                    },
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

    def _clean_row(self, row: dict[str, Any]) -> dict[str, str]:
        cleaned: dict[str, str] = {}
        for key, value in row.items():
            if key is None:
                continue
            normalized_key = self._normalize_key(key)
            text = str(value or "").strip()
            if normalized_key:
                cleaned[normalized_key] = text
        if not any(value for value in cleaned.values()):
            return {}
        return cleaned

    def _build_payload(
        self,
        row: dict[str, str],
        *,
        row_number: int,
        source: SourceConfig,
    ) -> dict[str, Any]:
        donor = self._pick(
            row,
            "donor",
            "donor_name",
            "name",
        )
        first_name = self._pick(row, "first_name", "donor_first_name")
        last_name = self._pick(row, "last_name", "donor_last_name")
        if donor and not first_name and not last_name:
            first_name = donor

        nonprofit_slug = self._pick(row, "nonprofit_slug", "slug") or source.config_json.get(
            "nonprofit_slug"
        )
        nonprofit_name = (
            self._pick(row, "nonprofit_name", "organization", "nonprofit")
            or source.source_name
        )
        nonprofit_ein = self._pick(row, "ein", "nonprofit_ein")

        fundraiser_title = self._pick(row, "fundraiser", "fundraiser_title", "campaign", "page")
        fundraiser_slug = self._pick(row, "fundraiser_slug")
        fundraiser_id = self._pick(row, "fundraiser_id")

        payment_method = self._pick(row, "payment_info", "payment_method")
        private_note = self._pick(row, "notes_testimony", "private_note", "notes")
        public_testimony = self._pick(row, "public_testimony", "testimony")
        designation = self._pick(row, "designation", "project")
        donation_date = self._normalize_date(
            self._pick(row, "created", "donation_date", "date", "created_at")
        )
        currency = self._pick(row, "currency") or self._infer_currency(
            self._pick(row, "donation", "donation_amount", "amount")
        )
        amount = self._normalize_amount(
            self._pick(row, "donation", "donation_amount", "amount")
        )
        net_amount = self._normalize_amount(self._pick(row, "net", "net_amount"))
        charge_id = self._pick(row, "charge_id", "donation_id", "id", "transaction_id")
        if not charge_id:
            charge_id = self._row_hash(
                row=row,
                row_number=row_number,
                filename=source.source_name,
            )

        payload: dict[str, Any] = {
            "chargeId": charge_id,
            "partnerDonationId": self._pick(row, "partner_donation_id", "external_id"),
            "firstName": first_name,
            "lastName": last_name,
            "email": self._pick(row, "email", "donor_email"),
            "toNonprofit": {
                "slug": nonprofit_slug,
                "ein": nonprofit_ein,
                "name": nonprofit_name,
            },
            "amount": amount,
            "netAmount": net_amount,
            "currency": currency or "USD",
            "frequency": self._normalize_frequency(self._pick(row, "frequency", "recurring")),
            "donationDate": donation_date,
            "designation": designation,
            "paymentMethod": payment_method,
            "privateNote": private_note,
            "publicTestimony": public_testimony,
            "_import": {
                "kind": "everyorg_dashboard_csv",
                "row_number": row_number,
                "original_row": row,
            },
        }
        if fundraiser_title or fundraiser_slug or fundraiser_id:
            derived_fundraiser_id = fundraiser_id or self._row_hash(
                row=row,
                row_number=row_number,
                filename="fundraiser",
            )
            payload["fromFundraiser"] = {
                "id": derived_fundraiser_id,
                "title": fundraiser_title or fundraiser_slug or "Dashboard fundraiser",
                "slug": fundraiser_slug or fundraiser_title or "dashboard-fundraiser",
            }
        return payload

    def _normalize_key(self, value: str) -> str:
        return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")

    def _pick(self, row: dict[str, str], *keys: str) -> str | None:
        for key in keys:
            value = row.get(key)
            if value and value.strip().lower() not in self._EMPTY_VALUES:
                return value.strip()
        return None

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

    def _normalize_frequency(self, value: str | None) -> str:
        if not value:
            return "One-time"
        lowered = value.strip().lower()
        if "month" in lowered:
            return "Monthly"
        if "year" in lowered or "annual" in lowered:
            return "Yearly"
        return "One-time"

    def _normalize_date(self, value: str | None) -> str:
        if not value:
            return datetime.now(tz=UTC).date().isoformat()
        parsed = self._parse_datetime(value)
        if parsed is not None:
            return parsed.isoformat().replace("+00:00", "Z")
        return value

    def _parse_datetime(self, value: Any) -> datetime | None:
        if not isinstance(value, str) or not value.strip():
            return None
        text = value.strip()
        for fmt in (
            "%m/%d/%Y",
            "%m/%d/%Y %H:%M",
            "%m/%d/%Y %I:%M %p",
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
        ):
            try:
                return datetime.strptime(text, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        try:
            return datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return None

    def _infer_currency(self, amount: str | None) -> str | None:
        if not amount:
            return None
        if "$" in amount:
            return "USD"
        return None

    def _row_hash(self, *, row: dict[str, str], row_number: int, filename: str | None) -> str:
        raw = f"{filename}|{row_number}|{sorted(row.items())}"
        digest = hashlib.sha1(raw.encode()).hexdigest()
        return digest[:24]
