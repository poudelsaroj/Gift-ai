"use client";

import { ActionBar } from "@/components/console/action-bar";
import { ActivityTab } from "@/components/console/activity-tab";
import { ConsoleTab } from "@/components/console/console-tab";
import { Hero } from "@/components/console/hero";
import { OverviewTab } from "@/components/console/overview-tab";
import { RecordsTab } from "@/components/console/records-tab";
import { Sidebar } from "@/components/console/sidebar";
import { TabStrip } from "@/components/console/tab-strip";
import { useOperatorConsole } from "@/hooks/use-operator-console";
import type { OperatorConsoleState, OperatorRecord } from "@/lib/types";

type OperatorConsoleProps = {
  initialConsoleState: OperatorConsoleState;
  initialRecords: OperatorRecord[];
};

export function OperatorConsole({
  initialConsoleState,
  initialRecords,
}: OperatorConsoleProps) {
  const {
    consoleState,
    selectedSourceId,
    activeTab,
    recordTypeFilter,
    recordStatusFilter,
    recordSearch,
    recordSortDirection,
    canonicalFile,
    everyOrgFile,
    busyAction,
    logs,
    selectedSource,
    filteredRecords,
    sourceRuns,
    sourceRecords,
    statusOptions,
    latestRun,
    mostRecentRecord,
    setSelectedSourceId,
    setActiveTab,
    setRecordTypeFilter,
    setRecordStatusFilter,
    setRecordSearch,
    setRecordSortDirection,
    setCanonicalFile,
    setEveryOrgFile,
    refreshData,
    handleAction,
    handleRunScheduler,
    handleCanonicalUpload,
    handleEveryOrgUpload,
  } = useOperatorConsole({ initialConsoleState, initialRecords });

  return (
    <div className="operator-shell">
      <Sidebar
        consoleState={consoleState}
        selectedSourceId={selectedSourceId}
        activeTab={activeTab}
        onSelectSource={setSelectedSourceId}
        onSelectTab={setActiveTab}
      />

      <main className="workspace">
        <Hero
          selectedSource={selectedSource}
          latestRun={latestRun}
          mostRecentRecord={mostRecentRecord}
        />
        <ActionBar
          selectedSource={selectedSource}
          busyAction={busyAction}
          onRefresh={() => void refreshData(false)}
          onRunScheduler={() => void handleRunScheduler()}
          onAction={(action) => void handleAction(action)}
        />
        <TabStrip activeTab={activeTab} onSelectTab={setActiveTab} />

        {activeTab === "overview" ? (
          <OverviewTab
            consoleState={consoleState}
            selectedSource={selectedSource}
            canonicalFile={canonicalFile}
            everyOrgFile={everyOrgFile}
            busyAction={busyAction}
            onCanonicalFileChange={setCanonicalFile}
            onEveryOrgFileChange={setEveryOrgFile}
            onCanonicalUpload={() => void handleCanonicalUpload()}
            onEveryOrgUpload={() => void handleEveryOrgUpload()}
          />
        ) : null}

        {activeTab === "activity" ? (
          <ActivityTab sourceRecords={sourceRecords} sourceRuns={sourceRuns} />
        ) : null}

        {activeTab === "records" ? (
          <RecordsTab
            filteredRecords={filteredRecords}
            recordTypeFilter={recordTypeFilter}
            recordStatusFilter={recordStatusFilter}
            recordSearch={recordSearch}
            statusOptions={statusOptions}
            recordSortDirection={recordSortDirection}
            onRecordTypeChange={setRecordTypeFilter}
            onRecordStatusChange={setRecordStatusFilter}
            onRecordSearchChange={setRecordSearch}
            onToggleSort={() =>
              setRecordSortDirection((current) => (current === "asc" ? "desc" : "asc"))
            }
          />
        ) : null}

        {activeTab === "console" ? <ConsoleTab logs={logs} /> : null}
      </main>
    </div>
  );
}
