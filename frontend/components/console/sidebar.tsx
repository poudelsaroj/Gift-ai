import type { OperatorConsoleState } from "@/lib/types";

import type { WorkspaceTab } from "@/components/console/types";
import { workspaceTabs } from "@/components/console/types";

type SidebarProps = {
  consoleState: OperatorConsoleState;
  selectedSourceId: number | null;
  activeTab: WorkspaceTab;
  onSelectSource: (sourceId: number | null) => void;
  onSelectTab: (tab: WorkspaceTab) => void;
};

export function Sidebar({
  consoleState,
  selectedSourceId,
  activeTab,
  onSelectSource,
  onSelectTab,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <span className="eyebrow">FastAPI backend</span>
        <h1>Gift Operator Console</h1>
        <p>Production workspace for sources, ingestion runs, imports, and canonical records.</p>
      </div>

      <div className="sidebar-section">
        <span className="sidebar-label">Workspace</span>
        <div className="tab-nav">
          {workspaceTabs.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={activeTab === tab.id ? "tab-link active" : "tab-link"}
              onClick={() => onSelectTab(tab.id)}
            >
              <strong>{tab.label}</strong>
              <span>{tab.detail}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="sidebar-section">
        <span className="sidebar-label">Source Control</span>
        <label className="field">
          <span>Active source</span>
          <select
            value={selectedSourceId ?? ""}
            onChange={(event) =>
              onSelectSource(event.target.value ? Number(event.target.value) : null)
            }
          >
            <option value="">All sources</option>
            {consoleState.sources.map((source) => (
              <option key={source.id} value={source.id}>
                {source.source_name} ({source.source_system})
              </option>
            ))}
          </select>
        </label>

        <div className="mini-stats">
          <article>
            <span>Sources</span>
            <strong>{consoleState.summary.total_sources}</strong>
          </article>
          <article>
            <span>Canonical records</span>
            <strong>{consoleState.summary.total_records}</strong>
          </article>
          <article>
            <span>Raw objects</span>
            <strong>{consoleState.summary.total_raw_objects}</strong>
          </article>
        </div>

        <div className="source-list">
          {consoleState.sources.map((source) => (
            <button
              key={source.id}
              type="button"
              className={selectedSourceId === source.id ? "source-card selected" : "source-card"}
              onClick={() => onSelectSource(source.id)}
            >
              <div className="source-card-top">
                <strong>{source.source_name}</strong>
                <span className={`pill ${source.enabled ? "success" : "danger"}`}>
                  {source.enabled ? "enabled" : "disabled"}
                </span>
              </div>
              <div className="source-card-meta">
                <span>{source.source_system}</span>
                <span>{source.acquisition_mode}</span>
              </div>
              <p>{source.workflow_label}</p>
            </button>
          ))}
        </div>
      </div>
    </aside>
  );
}
