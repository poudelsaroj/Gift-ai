import type { OperatorConsoleState, OperatorSourceSummary } from "@/lib/types";

type OverviewTabProps = {
  consoleState: OperatorConsoleState;
  selectedSource: OperatorSourceSummary | null;
  canonicalFile: File | null;
  everyOrgFile: File | null;
  busyAction: string | null;
  onCanonicalFileChange: (file: File | null) => void;
  onEveryOrgFileChange: (file: File | null) => void;
  onCanonicalUpload: () => void;
  onEveryOrgUpload: () => void;
};

export function OverviewTab({
  consoleState,
  selectedSource,
  canonicalFile,
  everyOrgFile,
  busyAction,
  onCanonicalFileChange,
  onEveryOrgFileChange,
  onCanonicalUpload,
  onEveryOrgUpload,
}: OverviewTabProps) {
  return (
    <section className="content-grid">
      <div className="panel-card">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Selected source</span>
            <h3>Operational summary</h3>
          </div>
        </div>
        <div className="stat-grid">
          <article className="stat-card">
            <span>System</span>
            <strong>{selectedSource?.source_system ?? "all"}</strong>
            <small>{selectedSource?.auth_type ?? "mixed backends"}</small>
          </article>
          <article className="stat-card">
            <span>Mode</span>
            <strong>{selectedSource?.acquisition_mode ?? "canonical"}</strong>
            <small>{selectedSource?.schedule ?? "manual"}</small>
          </article>
          <article className="stat-card">
            <span>Canonical rows</span>
            <strong>
              {selectedSource ? selectedSource.record_count : consoleState.summary.total_records}
            </strong>
            <small>
              {selectedSource
                ? `${selectedSource.gift_record_count} gift rows`
                : `${consoleState.summary.total_gift_records} gift rows`}
            </small>
          </article>
          <article className="stat-card">
            <span>Audit trail</span>
            <strong>
              {selectedSource
                ? selectedSource.raw_object_count
                : consoleState.summary.total_raw_objects}
            </strong>
            <small>{selectedSource?.raw_object_types.join(" • ") || "Mixed object types"}</small>
          </article>
        </div>
        <div className="callout">
          <strong>Integration details</strong>
          <p>
            {selectedSource?.workflow_label ??
              "The records table below is the common data model shared by every source."}
          </p>
        </div>
      </div>

      <div className="panel-card">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Uploads</span>
            <h3>Manual import tools</h3>
          </div>
        </div>
        <div className="upload-stack">
          <label className="upload-card">
            <span>Canonical CSV / XLSX upload</span>
            <input
              type="file"
              accept=".csv,.tsv,.xlsx"
              onChange={(event) => onCanonicalFileChange(event.target.files?.[0] ?? null)}
            />
            <small>
              For `csv/file_upload` sources this hits FastAPI&apos;s canonical import endpoint
              and lands in the shared model.
            </small>
          </label>
          <button
            type="button"
            className="accent"
            disabled={!selectedSource?.supports_manual_upload || !canonicalFile || busyAction !== null}
            onClick={onCanonicalUpload}
          >
            Upload and normalize
          </button>

          <label className="upload-card">
            <span>Every.org dashboard CSV</span>
            <input
              type="file"
              accept=".csv,text/csv"
              onChange={(event) => onEveryOrgFileChange(event.target.files?.[0] ?? null)}
            />
            <small>Historical Every.org donation backfills continue to run through FastAPI.</small>
          </label>
          <button
            type="button"
            className="secondary"
            disabled={selectedSource?.source_system !== "everyorg" || !everyOrgFile || busyAction !== null}
            onClick={onEveryOrgUpload}
          >
            Import dashboard CSV
          </button>
        </div>
      </div>

      <div className="panel-card full-width">
        <div className="panel-heading">
          <div>
            <span className="eyebrow">Redacted config</span>
            <h3>Selected source config</h3>
          </div>
        </div>
        <pre className="console-output">
          {JSON.stringify(
            selectedSource
              ? {
                  source_name: selectedSource.source_name,
                  parser_name: selectedSource.parser_name,
                  dedupe_keys: selectedSource.dedupe_keys,
                  notes: selectedSource.notes,
                  config_json: selectedSource.config_json,
                }
              : {
                  total_sources: consoleState.summary.total_sources,
                  systems: [...new Set(consoleState.sources.map((item) => item.source_system))],
                },
            null,
            2,
          )}
        </pre>
      </div>
    </section>
  );
}
