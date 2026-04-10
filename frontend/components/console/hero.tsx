import type { OperatorRecord, OperatorRun, OperatorSourceSummary } from "@/lib/types";
import { formatAmount, formatDateTime } from "@/lib/format";

type HeroProps = {
  selectedSource: OperatorSourceSummary | null;
  latestRun: OperatorRun | null;
  mostRecentRecord: OperatorRecord | null;
};

export function Hero({ selectedSource, latestRun, mostRecentRecord }: HeroProps) {
  return (
    <section className="hero-card">
      <div>
        <span className="eyebrow">Canonical operator workspace</span>
        <h2>{selectedSource ? selectedSource.source_name : "All sources"}</h2>
        <p>
          {selectedSource
            ? `${selectedSource.workflow_label}. Actions here affect only this source, while the records tab stays in the shared canonical model.`
            : "Cross-source view of ingestion health, normalized coverage, and manual imports. Select a source from the sidebar when you need source-specific actions."}
        </p>
        <div className="hero-links">
          <a href="http://127.0.0.1:8000/docs" target="_blank" rel="noreferrer">
            Swagger
          </a>
          <a href="http://127.0.0.1:8000/openapi.json" target="_blank" rel="noreferrer">
            OpenAPI
          </a>
          <a href="http://127.0.0.1:8000/api/v1/health" target="_blank" rel="noreferrer">
            Health
          </a>
        </div>
      </div>
      <div className="hero-summary">
        <article>
          <span>Latest run</span>
          <strong>{latestRun ? formatDateTime(latestRun.completed_at ?? latestRun.started_at) : "None"}</strong>
          <small>{latestRun ? `${latestRun.status} • ${latestRun.records_fetched_count} fetched` : "No runs yet"}</small>
        </article>
        <article>
          <span>Latest record</span>
          <strong>
            {mostRecentRecord
              ? mostRecentRecord.record_date ?? mostRecentRecord.gift_date ?? "Undated"
              : "No data"}
          </strong>
          <small>
            {mostRecentRecord
              ? `${mostRecentRecord.primary_name ?? mostRecentRecord.donor_name ?? "Unnamed"} • ${formatAmount(mostRecentRecord.amount, mostRecentRecord.currency)}`
              : "Import a file or run a source"}
          </small>
        </article>
      </div>
    </section>
  );
}
