import type { OperatorRecord } from "@/lib/types";
import { formatAmount, metadataSummary, statusClass } from "@/lib/format";

type RecordsTabProps = {
  filteredRecords: OperatorRecord[];
  recordTypeFilter: string;
  recordStatusFilter: string;
  recordSearch: string;
  statusOptions: string[];
  recordSortDirection: "asc" | "desc";
  onRecordTypeChange: (value: string) => void;
  onRecordStatusChange: (value: string) => void;
  onRecordSearchChange: (value: string) => void;
  onToggleSort: () => void;
};

export function RecordsTab({
  filteredRecords,
  recordTypeFilter,
  recordStatusFilter,
  recordSearch,
  statusOptions,
  recordSortDirection,
  onRecordTypeChange,
  onRecordStatusChange,
  onRecordSearchChange,
  onToggleSort,
}: RecordsTabProps) {
  return (
    <section className="panel-card">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">Canonical Records</span>
          <h3>Shared common data model</h3>
        </div>
      </div>

      <div className="filters">
        <label className="field">
          <span>Record type</span>
          <select value={recordTypeFilter} onChange={(event) => onRecordTypeChange(event.target.value)}>
            <option value="">All types</option>
            <option value="gift">Gift</option>
            <option value="supporter">Supporter</option>
          </select>
        </label>

        <label className="field">
          <span>Status</span>
          <select
            value={recordStatusFilter}
            onChange={(event) => onRecordStatusChange(event.target.value)}
          >
            <option value="">All statuses</option>
            {statusOptions.map((status) => (
              <option key={status} value={status}>
                {status}
              </option>
            ))}
          </select>
        </label>

        <label className="field search-field">
          <span>Search</span>
          <input
            value={recordSearch}
            onChange={(event) => onRecordSearchChange(event.target.value)}
            placeholder="Name, email, campaign, receipt, related entity"
          />
        </label>
      </div>

      <div className="table-shell">
        <table>
          <thead>
            <tr>
              <th>Source</th>
              <th>Type</th>
              <th>Record ID</th>
              <th>Name</th>
              <th>Email</th>
              <th>Campaign</th>
              <th>Related</th>
              <th>Amount</th>
              <th>
                <button type="button" className="sort-button" onClick={onToggleSort}>
                  Date {recordSortDirection === "asc" ? "↑" : "↓"}
                </button>
              </th>
              <th>Status</th>
              <th>Metadata</th>
            </tr>
          </thead>
          <tbody>
            {filteredRecords.map((record) => (
              <tr key={record.id}>
                <td>{record.source_name}</td>
                <td>{record.record_type ?? "-"}</td>
                <td>{record.source_record_id ?? record.gift_id ?? "-"}</td>
                <td>{record.primary_name ?? record.donor_name ?? "-"}</td>
                <td>{record.primary_email ?? record.donor_email ?? "-"}</td>
                <td>{record.campaign_name ?? record.challenge_name ?? "-"}</td>
                <td>{record.related_entity_name ?? record.participant_name ?? "-"}</td>
                <td>{formatAmount(record.amount, record.currency)}</td>
                <td>{record.record_date ?? record.gift_date ?? "-"}</td>
                <td>
                  <span className={`pill ${statusClass(record.status)}`}>{record.status ?? "n/a"}</span>
                </td>
                <td>{metadataSummary(record.extra_metadata)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
