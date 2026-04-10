"""Operator-console aggregation service."""

from __future__ import annotations

from collections import defaultdict
from datetime import date

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.ingestion_run import IngestionRun
from app.models.raw_object import RawObject
from app.models.source_config import SourceConfig
from app.models.staging_gift import StagingGift
from app.schemas.operator_console import (
    OperatorConsoleStateRead,
    OperatorConsoleSummaryRead,
    OperatorRecordRead,
    OperatorRunRead,
    OperatorSourceSummaryRead,
)
from app.utils.security import redact_config


class OperatorConsoleService:
    """Build UI-friendly source and record views."""

    def get_console_state(self, db: Session, *, recent_run_limit: int = 12) -> OperatorConsoleStateRead:
        sources = list(db.scalars(select(SourceConfig).order_by(SourceConfig.source_name.asc(), SourceConfig.id.asc())))
        source_ids = [source.id for source in sources]

        latest_runs = self._latest_runs_by_source(db, source_ids)
        raw_counts, raw_types = self._raw_metrics(db, source_ids)
        record_counts, gift_counts, latest_dates, status_values = self._record_metrics(db, source_ids)

        source_summaries = [
            OperatorSourceSummaryRead(
                id=source.id,
                source_name=source.source_name,
                source_system=source.source_system,
                acquisition_mode=source.acquisition_mode,
                auth_type=source.auth_type,
                enabled=source.enabled,
                schedule=source.schedule,
                parser_name=source.parser_name,
                dedupe_keys=source.dedupe_keys,
                notes=source.notes,
                config_json=redact_config(source.config_json or {}),
                created_at=source.created_at,
                updated_at=source.updated_at,
                workflow_label=self._workflow_label(source),
                primary_action_label=self._primary_action_label(source),
                supports_test_connection=True,
                supports_direct_trigger=self._supports_direct_trigger(source),
                supports_manual_upload=self._supports_manual_upload(source),
                supports_scheduler=bool(source.schedule and source.schedule != "manual"),
                special_actions=self._special_actions(source),
                latest_run=latest_runs.get(source.id),
                raw_object_count=raw_counts.get(source.id, 0),
                record_count=record_counts.get(source.id, 0),
                gift_record_count=gift_counts.get(source.id, 0),
                raw_object_types=sorted(raw_types.get(source.id, set())),
                record_status_values=sorted(status_values.get(source.id, set())),
                latest_record_date=latest_dates.get(source.id),
            )
            for source in sources
        ]

        recent_runs = self._recent_runs(db, limit=recent_run_limit)
        summary = OperatorConsoleSummaryRead(
            total_sources=len(source_summaries),
            total_records=sum(item.record_count for item in source_summaries),
            total_gift_records=sum(item.gift_record_count for item in source_summaries),
            total_raw_objects=sum(item.raw_object_count for item in source_summaries),
            latest_run_at=next(
                (
                    run.completed_at or run.started_at
                    for run in recent_runs
                    if run.completed_at or run.started_at
                ),
                None,
            ),
        )
        return OperatorConsoleStateRead(summary=summary, sources=source_summaries, recent_runs=recent_runs)

    def list_records(
        self,
        db: Session,
        *,
        source_id: int | None = None,
        record_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
        limit: int = 250,
    ) -> list[OperatorRecordRead]:
        query = (
            select(StagingGift, RawObject.source_id, SourceConfig.source_name)
            .join(RawObject, RawObject.id == StagingGift.raw_object_id)
            .join(SourceConfig, SourceConfig.id == RawObject.source_id)
        )
        if source_id is not None:
            query = query.where(RawObject.source_id == source_id)
        if record_type:
            query = query.where(StagingGift.record_type == record_type)
        if status:
            query = query.where(StagingGift.status == status)
        if search:
            like = f"%{search.strip()}%"
            query = query.where(
                or_(
                    StagingGift.source_system.ilike(like),
                    StagingGift.source_record_id.ilike(like),
                    StagingGift.primary_name.ilike(like),
                    StagingGift.primary_email.ilike(like),
                    StagingGift.donor_name.ilike(like),
                    StagingGift.donor_email.ilike(like),
                    StagingGift.campaign_name.ilike(like),
                    StagingGift.challenge_name.ilike(like),
                    StagingGift.related_entity_name.ilike(like),
                    StagingGift.team_name.ilike(like),
                    StagingGift.receipt_number.ilike(like),
                )
            )
        query = query.order_by(
            func.coalesce(StagingGift.record_date, StagingGift.gift_date).desc(),
            StagingGift.id.desc(),
        ).limit(limit)

        rows = db.execute(query).all()
        return [
            OperatorRecordRead(
                id=record.id,
                raw_object_id=record.raw_object_id,
                source_id=resolved_source_id,
                source_name=source_name,
                record_type=record.record_type,
                source_record_id=record.source_record_id,
                source_parent_id=record.source_parent_id,
                gift_id=record.gift_id,
                source_channel=record.source_channel,
                source_system=record.source_system,
                source_file_id=record.source_file_id,
                primary_name=record.primary_name,
                primary_email=record.primary_email,
                donor_name=record.donor_name,
                donor_email=record.donor_email,
                company_name=record.company_name,
                amount=record.amount,
                currency=record.currency,
                record_date=record.record_date,
                gift_date=record.gift_date,
                payment_type=record.payment_type,
                gift_type=record.gift_type,
                campaign_id=record.campaign_id,
                campaign_name=record.campaign_name,
                challenge_id=record.challenge_id,
                challenge_name=record.challenge_name,
                related_entity_id=record.related_entity_id,
                related_entity_name=record.related_entity_name,
                participant_id=record.participant_id,
                participant_name=record.participant_name,
                team_id=record.team_id,
                team_name=record.team_name,
                charity_id=record.charity_id,
                receipt_number=record.receipt_number,
                memo=record.memo,
                raw_payload_ref=record.raw_payload_ref,
                status=record.status,
                duplicate_status=record.duplicate_status,
                confidence_score=record.confidence_score,
                extra_metadata=record.extra_metadata,
                created_at=record.created_at,
                updated_at=record.updated_at,
            )
            for record, resolved_source_id, source_name in rows
        ]

    def _latest_runs_by_source(self, db: Session, source_ids: list[int]) -> dict[int, OperatorRunRead]:
        if not source_ids:
            return {}
        latest_ids = (
            select(func.max(IngestionRun.id).label("latest_id"))
            .where(IngestionRun.source_id.in_(source_ids))
            .group_by(IngestionRun.source_id)
            .subquery()
        )
        rows = db.execute(
            select(IngestionRun, SourceConfig.source_name, SourceConfig.source_system)
            .join(SourceConfig, SourceConfig.id == IngestionRun.source_id)
            .where(IngestionRun.id.in_(select(latest_ids.c.latest_id)))
        ).all()
        return {
            run.source_id: self._run_read(run, source_name=source_name, source_system=source_system)
            for run, source_name, source_system in rows
        }

    def _recent_runs(self, db: Session, *, limit: int) -> list[OperatorRunRead]:
        rows = db.execute(
            select(IngestionRun, SourceConfig.source_name, SourceConfig.source_system)
            .join(SourceConfig, SourceConfig.id == IngestionRun.source_id)
            .order_by(IngestionRun.id.desc())
            .limit(limit)
        ).all()
        return [
            self._run_read(run, source_name=source_name, source_system=source_system)
            for run, source_name, source_system in rows
        ]

    def _raw_metrics(
        self,
        db: Session,
        source_ids: list[int],
    ) -> tuple[dict[int, int], dict[int, set[str]]]:
        raw_counts: dict[int, int] = {}
        raw_types: dict[int, set[str]] = defaultdict(set)
        if not source_ids:
            return raw_counts, raw_types
        count_rows = db.execute(
            select(RawObject.source_id, func.count(RawObject.id))
            .where(RawObject.source_id.in_(source_ids))
            .group_by(RawObject.source_id)
        ).all()
        for source_id, count in count_rows:
            raw_counts[int(source_id)] = int(count or 0)
        type_rows = db.execute(
            select(RawObject.source_id, RawObject.external_object_type)
            .where(RawObject.source_id.in_(source_ids))
            .distinct()
        ).all()
        for source_id, object_type in type_rows:
            if object_type:
                raw_types[int(source_id)].add(str(object_type))
        return raw_counts, raw_types

    def _record_metrics(
        self,
        db: Session,
        source_ids: list[int],
    ) -> tuple[dict[int, int], dict[int, int], dict[int, date], dict[int, set[str]]]:
        record_counts: dict[int, int] = {}
        gift_counts: dict[int, int] = {}
        latest_dates: dict[int, date] = {}
        status_values: dict[int, set[str]] = defaultdict(set)
        if not source_ids:
            return record_counts, gift_counts, latest_dates, status_values

        count_rows = db.execute(
            select(RawObject.source_id, func.count(StagingGift.id))
            .join(RawObject, RawObject.id == StagingGift.raw_object_id)
            .where(RawObject.source_id.in_(source_ids))
            .group_by(RawObject.source_id)
        ).all()
        for source_id, count in count_rows:
            record_counts[int(source_id)] = int(count or 0)

        gift_rows = db.execute(
            select(RawObject.source_id, func.count(StagingGift.id))
            .join(RawObject, RawObject.id == StagingGift.raw_object_id)
            .where(RawObject.source_id.in_(source_ids), StagingGift.record_type == "gift")
            .group_by(RawObject.source_id)
        ).all()
        for source_id, count in gift_rows:
            gift_counts[int(source_id)] = int(count or 0)

        date_rows = db.execute(
            select(
                RawObject.source_id,
                func.max(func.coalesce(StagingGift.record_date, StagingGift.gift_date)),
            )
            .join(RawObject, RawObject.id == StagingGift.raw_object_id)
            .where(RawObject.source_id.in_(source_ids))
            .group_by(RawObject.source_id)
        ).all()
        for source_id, latest_date in date_rows:
            latest_dates[int(source_id)] = latest_date

        status_rows = db.execute(
            select(RawObject.source_id, StagingGift.status)
            .join(RawObject, RawObject.id == StagingGift.raw_object_id)
            .where(RawObject.source_id.in_(source_ids), StagingGift.status.is_not(None))
            .distinct()
        ).all()
        for source_id, status in status_rows:
            if status:
                status_values[int(source_id)].add(str(status))
        return record_counts, gift_counts, latest_dates, status_values

    def _run_read(self, run: IngestionRun, *, source_name: str, source_system: str) -> OperatorRunRead:
        return OperatorRunRead(
            id=run.id,
            source_id=run.source_id,
            source_name=source_name,
            source_system=source_system,
            run_type=run.run_type,
            trigger_type=run.trigger_type,
            status=run.status,
            started_at=run.started_at,
            completed_at=run.completed_at,
            records_fetched_count=run.records_fetched_count,
            duplicates_detected_count=run.duplicates_detected_count,
            error_message=run.error_message,
        )

    def _workflow_label(self, source: SourceConfig) -> str:
        if source.source_system == "gmail":
            return "Mailbox polling and attachment extraction"
        if source.source_system == "csv":
            return "Manual CSV, TSV, or XLSX import"
        if source.source_system == "everyorg":
            return "Webhook intake plus dashboard CSV backfill"
        if source.source_system == "onecause":
            return "Authenticated API sync for events, supporters, and gifts"
        if source.acquisition_mode == "webhook":
            return "Webhook intake"
        return f"{source.acquisition_mode or 'manual'} ingestion"

    def _primary_action_label(self, source: SourceConfig) -> str:
        if self._supports_manual_upload(source):
            return "Upload file"
        if source.source_system == "gmail":
            return "Poll mailbox"
        if source.source_system == "pledge":
            return "Pull donations"
        if source.source_system == "onecause":
            return "Run sync"
        if source.acquisition_mode == "webhook":
            return "Await webhook"
        return "Run sync"

    def _supports_manual_upload(self, source: SourceConfig) -> bool:
        return source.source_system == "csv" and source.acquisition_mode == "file_upload"

    def _supports_direct_trigger(self, source: SourceConfig) -> bool:
        return source.acquisition_mode != "webhook" and not self._supports_manual_upload(source)

    def _special_actions(self, source: SourceConfig) -> list[str]:
        if source.source_system == "onecause":
            return ["paid_activities", "supporters", "full_sync"]
        if source.source_system == "everyorg":
            return ["dashboard_csv_import", "webhook"]
        if self._supports_manual_upload(source):
            return ["canonical_file_import"]
        return []
