"use client";

import { useEffect, useMemo, useState } from "react";

import type { LogItem, WorkspaceTab } from "@/components/console/types";
import {
  fetchConsoleState,
  fetchRecords,
  importCanonicalFile,
  importEveryOrgDashboard,
  runScheduler,
  runSourceAction,
} from "@/lib/api";
import { sortRecordsByDate } from "@/lib/format";
import type { OperatorConsoleState, OperatorRecord, SourceAction } from "@/lib/types";

type UseOperatorConsoleOptions = {
  initialConsoleState: OperatorConsoleState;
  initialRecords: OperatorRecord[];
};

export function useOperatorConsole({
  initialConsoleState,
  initialRecords,
}: UseOperatorConsoleOptions) {
  const [consoleState, setConsoleState] = useState(initialConsoleState);
  const [records, setRecords] = useState(initialRecords);
  const [selectedSourceId, setSelectedSourceId] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<WorkspaceTab>("overview");
  const [recordTypeFilter, setRecordTypeFilter] = useState("");
  const [recordStatusFilter, setRecordStatusFilter] = useState("");
  const [recordSearch, setRecordSearch] = useState("");
  const [recordSortDirection, setRecordSortDirection] = useState<"asc" | "desc">("desc");
  const [canonicalFile, setCanonicalFile] = useState<File | null>(null);
  const [everyOrgFile, setEveryOrgFile] = useState<File | null>(null);
  const [busyAction, setBusyAction] = useState<string | null>(null);
  const [logs, setLogs] = useState<LogItem[]>([]);

  const selectedSource = useMemo(
    () => consoleState.sources.find((item) => item.id === selectedSourceId) ?? null,
    [consoleState.sources, selectedSourceId],
  );

  const filteredRecords = useMemo(() => {
    const sourceScoped = selectedSource
      ? records.filter((item) => item.source_id === selectedSource.id)
      : records;
    const searched = sourceScoped.filter((item) => {
      const haystack = [
        item.source_name,
        item.source_system,
        item.source_record_id,
        item.primary_name,
        item.primary_email,
        item.donor_name,
        item.donor_email,
        item.campaign_name,
        item.related_entity_name,
        item.receipt_number,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();
      const matchesSearch = recordSearch ? haystack.includes(recordSearch.toLowerCase()) : true;
      const matchesType = recordTypeFilter ? item.record_type === recordTypeFilter : true;
      const matchesStatus = recordStatusFilter ? item.status === recordStatusFilter : true;
      return matchesSearch && matchesType && matchesStatus;
    });

    return sortRecordsByDate(searched, recordSortDirection);
  }, [
    records,
    selectedSource,
    recordSearch,
    recordStatusFilter,
    recordTypeFilter,
    recordSortDirection,
  ]);

  const sourceRuns = useMemo(() => {
    if (!selectedSource) return consoleState.recent_runs;
    return consoleState.recent_runs.filter((item) => item.source_id === selectedSource.id);
  }, [consoleState.recent_runs, selectedSource]);

  const sourceRecords = useMemo(() => {
    if (!selectedSource) return records;
    return records.filter((item) => item.source_id === selectedSource.id);
  }, [records, selectedSource]);

  const statusOptions = useMemo(() => {
    const values = new Set<string>();
    consoleState.sources.forEach((source) => {
      source.record_status_values.forEach((status) => values.add(status));
    });
    records.forEach((record) => {
      if (record.status) values.add(record.status);
    });
    return [...values].sort();
  }, [consoleState.sources, records]);

  const latestRun = selectedSource?.latest_run ?? consoleState.recent_runs[0] ?? null;
  const mostRecentRecord = sourceRecords[0] ?? null;

  useEffect(() => {
    const timer = window.setInterval(() => {
      void refreshData(true);
    }, 15000);
    return () => window.clearInterval(timer);
  });

  function appendLog(title: string, payload: unknown) {
    setLogs((current) => [
      {
        id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
        title,
        payload,
        timestamp: new Date().toLocaleTimeString(),
      },
      ...current,
    ]);
  }

  async function refreshData(silent = false) {
    try {
      const [nextConsoleState, nextRecords] = await Promise.all([
        fetchConsoleState(),
        fetchRecords({ limit: 500 }),
      ]);
      setConsoleState(nextConsoleState);
      setRecords(nextRecords);
      if (!silent) {
        appendLog("Refreshed operator state", {
          sources: nextConsoleState.sources.length,
          recentRuns: nextConsoleState.recent_runs.length,
          records: nextRecords.length,
        });
      }
    } catch (error) {
      appendLog("Refresh failed", error instanceof Error ? error.message : String(error));
      throw error;
    }
  }

  async function handleAction(action: SourceAction) {
    if (!selectedSource) {
      appendLog("Action blocked", "Select a source first.");
      return;
    }
    setBusyAction(`${action}:${selectedSource.id}`);
    try {
      const result = await runSourceAction(selectedSource.id, action);
      appendLog(`Ran ${action} action`, result);
      await refreshData(true);
    } catch (error) {
      appendLog(`${action} failed`, error instanceof Error ? error.message : String(error));
    } finally {
      setBusyAction(null);
    }
  }

  async function handleRunScheduler() {
    setBusyAction("scheduler");
    try {
      const result = await runScheduler();
      appendLog("Ran scheduler", result);
      await refreshData(true);
    } catch (error) {
      appendLog("Scheduler failed", error instanceof Error ? error.message : String(error));
    } finally {
      setBusyAction(null);
    }
  }

  async function handleCanonicalUpload() {
    if (!selectedSource || !canonicalFile) {
      appendLog("Canonical import blocked", "Select a CSV source and attach a file.");
      return;
    }
    setBusyAction("canonical-upload");
    try {
      const result = await importCanonicalFile(selectedSource.id, canonicalFile);
      appendLog("Imported canonical file", result);
      setCanonicalFile(null);
      await refreshData(true);
      setActiveTab("records");
    } catch (error) {
      appendLog("Canonical import failed", error instanceof Error ? error.message : String(error));
    } finally {
      setBusyAction(null);
    }
  }

  async function handleEveryOrgUpload() {
    if (!selectedSource || !everyOrgFile) {
      appendLog("Every.org import blocked", "Select an Every.org source and attach a file.");
      return;
    }
    setBusyAction("everyorg-upload");
    try {
      const result = await importEveryOrgDashboard(selectedSource.id, everyOrgFile);
      appendLog("Imported Every.org dashboard file", result);
      setEveryOrgFile(null);
      await refreshData(true);
      setActiveTab("activity");
    } catch (error) {
      appendLog(
        "Every.org dashboard import failed",
        error instanceof Error ? error.message : String(error),
      );
    } finally {
      setBusyAction(null);
    }
  }

  return {
    consoleState,
    records,
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
  };
}
