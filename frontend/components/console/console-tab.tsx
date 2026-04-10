import type { LogItem } from "@/components/console/types";

type ConsoleTabProps = {
  logs: LogItem[];
};

export function ConsoleTab({ logs }: ConsoleTabProps) {
  return (
    <section className="panel-card">
      <div className="panel-heading">
        <div>
          <span className="eyebrow">Operator log</span>
          <h3>Action console</h3>
        </div>
      </div>
      <div className="stack-list">
        {logs.length === 0 ? (
          <article className="list-card">
            <strong>No actions yet</strong>
            <span>Refresh, run a source, or import a file to populate the log.</span>
          </article>
        ) : (
          logs.map((item) => (
            <article key={item.id} className="list-card">
              <div className="list-row">
                <strong>{item.title}</strong>
                <span>{item.timestamp}</span>
              </div>
              <pre className="console-output">{JSON.stringify(item.payload, null, 2)}</pre>
            </article>
          ))
        )}
      </div>
    </section>
  );
}
