import type {
  OperatorConsoleState,
  OperatorRecord,
  RecordFilters,
  SourceAction,
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ?? "http://127.0.0.1:8000";

async function apiRequest<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function fetchConsoleState(): Promise<OperatorConsoleState> {
  return apiRequest<OperatorConsoleState>("/api/v1/ui/console-state");
}

export function fetchRecords(filters: RecordFilters = {}): Promise<OperatorRecord[]> {
  const params = new URLSearchParams();
  if (filters.sourceId) params.set("source_id", String(filters.sourceId));
  if (filters.recordType) params.set("record_type", filters.recordType);
  if (filters.status) params.set("status", filters.status);
  if (filters.search) params.set("search", filters.search);
  params.set("limit", String(filters.limit ?? 500));
  return apiRequest<OperatorRecord[]>(`/api/v1/ui/records?${params.toString()}`);
}

export function runScheduler(): Promise<unknown> {
  return apiRequest("/api/v1/scheduler/run-due?force=true", { method: "POST" });
}

export function runSourceAction(sourceId: number, action: SourceAction): Promise<unknown> {
  const routeMap: Record<SourceAction, string> = {
    test: `/api/v1/sources/${sourceId}/test`,
    paid: `/api/v1/sources/${sourceId}/sync/onecause/paid-activities`,
    supporters: `/api/v1/sources/${sourceId}/sync/onecause/supporters`,
    full: `/api/v1/sources/${sourceId}/trigger`,
  };
  return apiRequest(routeMap[action], {
    method: "POST",
    body:
      action === "full"
        ? JSON.stringify({ run_type: "incremental", trigger_type: "manual" })
        : undefined,
  });
}

export function importCanonicalFile(sourceId: number, file: File): Promise<unknown> {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest(`/api/v1/files/sources/${sourceId}/imports/canonical`, {
    method: "POST",
    body: formData,
  });
}

export function importEveryOrgDashboard(sourceId: number, file: File): Promise<unknown> {
  const formData = new FormData();
  formData.append("file", file);
  return apiRequest(`/api/v1/everyorg/dashboard/sources/${sourceId}/imports/donations`, {
    method: "POST",
    body: formData,
  });
}
