import type { WorkspaceTab } from "@/components/console/types";
import { workspaceTabs } from "@/components/console/types";

type TabStripProps = {
  activeTab: WorkspaceTab;
  onSelectTab: (tab: WorkspaceTab) => void;
};

export function TabStrip({ activeTab, onSelectTab }: TabStripProps) {
  return (
    <section className="tab-strip">
      {workspaceTabs.map((tab) => (
        <button
          key={tab.id}
          type="button"
          className={activeTab === tab.id ? "workspace-tab active" : "workspace-tab"}
          onClick={() => onSelectTab(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </section>
  );
}
