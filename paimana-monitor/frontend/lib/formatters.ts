/**
 * Formatting utilities — currency, dates, percentages, risk labels.
 */

export function formatCurrency(value?: number | null, unit = "₹ Lakhs"): string {
  if (value == null) return "—";
  if (value >= 100) {
    return `₹ ${(value / 100).toLocaleString("en-IN", { maximumFractionDigits: 2 })} Cr`;
  }
  return `₹ ${value.toLocaleString("en-IN", { maximumFractionDigits: 2 })} L`;
}

export function formatProgress(value?: number | null): string {
  if (value == null) return "—";
  return `${value.toFixed(1)}%`;
}

export function formatDate(value?: string | null): string {
  if (!value) return "—";
  const d = new Date(value);
  return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" });
}

export function formatMonth(value?: string | null): string {
  if (!value) return "—";
  const d = new Date(value);
  return d.toLocaleDateString("en-IN", { month: "long", year: "numeric" });
}

export function formatNumber(value?: number | null): string {
  if (value == null) return "—";
  return value.toLocaleString("en-IN");
}

export function formatDays(days?: number | null): string {
  if (days == null) return "—";
  if (Math.abs(days) >= 30) {
    const months = Math.round(days / 30);
    return `${months} month${Math.abs(months) !== 1 ? "s" : ""}`;
  }
  return `${days} day${Math.abs(days) !== 1 ? "s" : ""}`;
}

// ─── Risk ──────────────────────────────────────────────────────────────────

export type RiskLevel = "low" | "medium" | "high" | "critical";

export const RISK_COLORS: Record<string, string> = {
  low: "#22c55e",
  medium: "#f59e0b",
  high: "#ef4444",
  critical: "#7c3aed",
};

export const RISK_BG: Record<string, string> = {
  low: "bg-green-100 text-green-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-red-100 text-red-800",
  critical: "bg-purple-100 text-purple-800",
};

export const RISK_LABELS: Record<string, string> = {
  low: "Low Risk",
  medium: "Medium Risk",
  high: "High Risk",
  critical: "Critical Risk",
};

export const STATUS_LABELS: Record<string, string> = {
  ongoing: "Ongoing",
  completed: "Completed",
  stalled: "Stalled",
  abandoned: "Abandoned",
  not_started: "Not Started",
  unknown: "Unknown",
};

export const STATUS_BG: Record<string, string> = {
  ongoing: "bg-blue-100 text-blue-800",
  completed: "bg-green-100 text-green-800",
  stalled: "bg-red-100 text-red-800",
  abandoned: "bg-gray-100 text-gray-800",
  not_started: "bg-gray-100 text-gray-600",
  unknown: "bg-gray-100 text-gray-500",
};

export const ALERT_SEVERITY_BG: Record<string, string> = {
  low: "bg-blue-100 text-blue-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-red-100 text-red-800",
  critical: "bg-purple-100 text-purple-800 border border-purple-300",
};

export const SECTOR_COLORS = [
  "#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6",
  "#06b6d4", "#f97316", "#84cc16", "#ec4899", "#14b8a6",
];
