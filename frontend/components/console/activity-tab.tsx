import type { OperatorRecord, OperatorRun } from "@/lib/types";
import { formatAmount, formatDateTime, statusClass } from "@/lib/format";

type ActivityTabProps = {
  sourceRecords: OperatorRecord[];
  sourceRuns: OperatorRun[];
};

export function ActivityTab({ sourceRecords, sourceRuns }: ActivityTabProps) {
  return (
    <section className="content-grid">
      <div className="panel-card">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Recent records</span>
            <h3>Latest normalized rows</h3>
          </div>
        </div>
        <div className="stack-list">
          {sourceRecords.slice(0, 6).map((record) => (
            <article key={record.id} className="list-card">
              <strong>{record.primary_name ?? record.donor_name ?? record.source_record_id}</strong>
              <span>{record.primary_email ?? record.donor_email ?? "No email"}</span>
              <small>
                {formatAmount(record.amount, record.currency)} •{" "}
                {record.record_date ?? record.gift_date ?? "No date"}
              </small>
            </article>
          ))}
        </div>
      </div>

      <div className="panel-card">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Run history</span>
            <h3>Recent runs</h3>
          </div>
        </div>
        <div className="stack-list">
          {sourceRuns.slice(0, 8).map((run) => (
            <article key={run.id} className="list-card">
              <div className="list-row">
                <strong>{run.source_name}</strong>
                <span className={`pill ${statusClass(run.status)}`}>{run.status}</span>
              </div>
              <span>
                {run.trigger_type} • {run.run_type}
              </span>
              <small>
                {formatDateTime(run.completed_at ?? run.started_at)} • {run.records_fetched_count} fetched •{" "}
                {run.duplicates_detected_count} duplicates
              </small>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
