import type { OperatorRecord } from "@/lib/types";

export function formatDateTime(value: string | null) {
  if (!value) return "No activity";
  return new Date(value).toLocaleString();
}

export function formatAmount(amount: string | number | null, currency: string | null) {
  if (amount === null || amount === undefined || amount === "") return "No amount";
  return `${amount} ${currency ?? ""}`.trim();
}

export function metadataSummary(value: Record<string, unknown> | null) {
  if (!value) return "No metadata";
  return Object.entries(value)
    .filter(([, current]) => current !== null && current !== "")
    .slice(0, 3)
    .map(([key]) => key)
    .join(", ");
}

export function statusClass(status: string | null | undefined) {
  if (!status) return "neutral";
  if (["completed", "succeeded", "enabled", "active", "extracted"].includes(status)) {
    return "success";
  }
  if (["failed", "disabled"].includes(status)) {
    return "danger";
  }
  return "warning";
}

export function sortRecordsByDate(
  records: OperatorRecord[],
  direction: "asc" | "desc",
): OperatorRecord[] {
  return records.slice().sort((left, right) => {
    const leftValue = new Date(left.record_date ?? left.gift_date ?? 0).getTime() || 0;
    const rightValue = new Date(right.record_date ?? right.gift_date ?? 0).getTime() || 0;
    return direction === "asc" ? leftValue - rightValue : rightValue - leftValue;
  });
}
