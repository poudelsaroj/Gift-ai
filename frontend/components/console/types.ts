export type WorkspaceTab = "overview" | "activity" | "records" | "console";

export type LogItem = {
  id: string;
  title: string;
  payload: unknown;
  timestamp: string;
};

export const workspaceTabs: Array<{
  id: WorkspaceTab;
  label: string;
  detail: string;
}> = [
  { id: "overview", label: "Overview", detail: "Source controls, config, and imports" },
  { id: "activity", label: "Activity", detail: "Run history and recent normalized records" },
  { id: "records", label: "Records", detail: "Canonical review table" },
  { id: "console", label: "Console", detail: "Request and action log" },
];
