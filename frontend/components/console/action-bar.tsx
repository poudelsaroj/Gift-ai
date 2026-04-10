import type { OperatorSourceSummary } from "@/lib/types";

type ActionBarProps = {
  selectedSource: OperatorSourceSummary | null;
  busyAction: string | null;
  onRefresh: () => void;
  onRunScheduler: () => void;
  onAction: (action: "test" | "paid" | "supporters" | "full") => void;
};

export function ActionBar({
  selectedSource,
  busyAction,
  onRefresh,
  onRunScheduler,
  onAction,
}: ActionBarProps) {
  return (
    <section className="action-bar">
      <div className="action-group">
        <button type="button" className="ghost" onClick={onRefresh} disabled={busyAction !== null}>
          Refresh
        </button>
        <button
          type="button"
          className="ghost"
          onClick={onRunScheduler}
          disabled={busyAction !== null}
        >
          Run scheduled sources now
        </button>
      </div>
      <div className="action-group">
        <button
          type="button"
          className="ghost"
          onClick={() => onAction("test")}
          disabled={!selectedSource || busyAction !== null}
        >
          Test connection
        </button>
        <button
          type="button"
          onClick={() => onAction("paid")}
          disabled={!selectedSource || selectedSource.source_system !== "onecause" || busyAction !== null}
        >
          Paid activities
        </button>
        <button
          type="button"
          className="secondary"
          onClick={() => onAction("supporters")}
          disabled={!selectedSource || selectedSource.source_system !== "onecause" || busyAction !== null}
        >
          Supporters
        </button>
        <button
          type="button"
          className="accent"
          onClick={() => onAction("full")}
          disabled={!selectedSource?.supports_direct_trigger || busyAction !== null}
        >
          {selectedSource?.source_system === "gmail"
            ? "Poll mailbox"
            : selectedSource?.source_system === "pledge"
              ? "Pull donations"
              : "Run sync"}
        </button>
      </div>
    </section>
  );
}
