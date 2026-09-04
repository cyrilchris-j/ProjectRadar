"use client";

import { useEffect, useState, useCallback } from "react";
import { listAlerts, resolveAlert, getAlertsSummary, type Alert } from "@/lib/api";
import { formatDate } from "@/lib/formatters";
import clsx from "clsx";
import Link from "next/link";

const SEVERITY_ORDER = ["critical", "high", "medium", "low"];

function AlertCard({
  alert,
  onResolve,
}: {
  alert: Alert;
  onResolve: (id: string) => void;
}) {
  const [resolving, setResolving] = useState(false);
  const [note, setNote] = useState("");
  const [showResolve, setShowResolve] = useState(false);

  const handleResolve = async () => {
    if (!note.trim()) return;
    setResolving(true);
    try {
      await resolveAlert(alert.id, note);
      onResolve(alert.id);
    } finally {
      setResolving(false);
    }
  };

  const severityClass =
    alert.severity === "critical" ? "border-l-purple-500 bg-purple-500/5" :
    alert.severity === "high" ? "border-l-red-500 bg-red-500/5" :
    alert.severity === "medium" ? "border-l-amber-500 bg-amber-500/5" :
    "border-l-blue-500 bg-blue-500/5";

  const severityBadge =
    alert.severity === "critical" ? "bg-purple-500/20 text-purple-400 border-purple-500/30" :
    alert.severity === "high" ? "bg-red-500/20 text-red-400 border-red-500/30" :
    alert.severity === "medium" ? "bg-amber-500/20 text-amber-400 border-amber-500/30" :
    "bg-blue-500/20 text-blue-400 border-blue-500/30";

  return (
    <div className={clsx("card border-l-4 p-4 space-y-3", severityClass)}>
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className={clsx(
              "text-[10px] font-bold uppercase tracking-widest px-2 py-0.5 rounded border",
              severityBadge
            )}>
              {alert.severity}
            </span>
            <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded capitalize">
              {alert.alert_type.replace(/_/g, " ")}
            </span>
          </div>
          <h3 className="text-sm font-semibold text-slate-200 mt-1.5 leading-snug">
            {alert.title}
          </h3>
          {alert.project_name && (
            <Link
              href={`/dashboard/projects/${alert.project_id}`}
              className="text-xs text-blue-400 hover:text-blue-300 transition-colors"
            >
              {alert.project_name}
            </Link>
          )}
        </div>
        <span className="text-xs text-slate-600 flex-shrink-0">{formatDate(alert.created_at)}</span>
      </div>

      {/* Description */}
      <p className="text-sm text-slate-400 leading-relaxed">{alert.description}</p>

      {/* Recommended action */}
      {alert.recommended_action && (
        <div className="text-xs text-slate-500 bg-slate-900/60 px-3 py-2 rounded border border-slate-800">
          <span className="font-semibold text-slate-400">Action: </span>
          {alert.recommended_action}
        </div>
      )}

      {/* Evidence */}
      {alert.evidence && Object.keys(alert.evidence).length > 0 && (
        <details className="text-xs">
          <summary className="text-slate-500 cursor-pointer hover:text-slate-400 transition-colors">
            View evidence data
          </summary>
          <div className="mt-2 p-2 bg-slate-900 rounded font-mono text-slate-400 overflow-x-auto">
            {Object.entries(alert.evidence).map(([k, v]) => (
              <div key={k}>
                <span className="text-slate-500">{k}: </span>
                <span>{JSON.stringify(v)}</span>
              </div>
            ))}
          </div>
        </details>
      )}

      {/* Resolve */}
      {!alert.is_resolved && (
        <div>
          {!showResolve ? (
            <button
              className="btn-ghost text-xs py-1.5 px-3"
              onClick={() => setShowResolve(true)}
              id={`resolve-btn-${alert.id.slice(0, 8)}`}
            >
              Mark as Resolved
            </button>
          ) : (
            <div className="flex gap-2 items-center">
              <input
                className="input text-sm flex-1"
                placeholder="Resolution note (required)…"
                value={note}
                onChange={(e) => setNote(e.target.value)}
              />
              <button
                className="btn-primary text-sm py-1.5 px-3"
                onClick={handleResolve}
                disabled={resolving || !note.trim()}
              >
                {resolving ? "…" : "Resolve"}
              </button>
              <button
                className="btn-ghost text-sm py-1.5"
                onClick={() => setShowResolve(false)}
              >
                Cancel
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [summary, setSummary] = useState<Record<string, number>>({});
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [showResolved, setShowResolved] = useState(false);
  const [severityFilter, setSeverityFilter] = useState("");

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const [alertsRes, sum] = await Promise.all([
        listAlerts({
          page,
          limit: 15,
          severity: severityFilter || undefined,
          is_resolved: showResolved,
        }),
        getAlertsSummary(),
      ]);
      setAlerts(alertsRes.data);
      setTotal(alertsRes.pagination.total);
      setSummary(sum);
    } finally {
      setIsLoading(false);
    }
  }, [page, severityFilter, showResolved]);

  useEffect(() => { load(); }, [load]);

  const handleResolve = (id: string) => {
    setAlerts((prev) => prev.filter((a) => a.id !== id));
    setSummary((prev) => ({ ...prev, total: (prev.total || 1) - 1 }));
  };

  const totalPages = Math.max(1, Math.ceil(total / 15));

  return (
    <div className="space-y-5 max-w-5xl mx-auto">
      {/* Header */}
      <div>
        <h1 className="text-xl font-bold text-slate-100">Early Warning Alerts</h1>
        <p className="text-sm text-slate-500 mt-0.5">
          Automated risk flags generated by the rule-based detection engine
        </p>
      </div>

      {/* Summary badges */}
      <div className="flex flex-wrap gap-3">
        {[
          { label: "Critical", key: "critical", cls: "border-purple-500/30 text-purple-400 bg-purple-500/10" },
          { label: "High", key: "high", cls: "border-red-500/30 text-red-400 bg-red-500/10" },
          { label: "Medium", key: "medium", cls: "border-amber-500/30 text-amber-400 bg-amber-500/10" },
          { label: "Low", key: "low", cls: "border-blue-500/30 text-blue-400 bg-blue-500/10" },
        ].map((s) => (
          <button
            key={s.key}
            onClick={() => setSeverityFilter(severityFilter === s.key ? "" : s.key)}
            className={clsx(
              "px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all",
              s.cls,
              severityFilter === s.key ? "ring-2 ring-offset-2 ring-offset-slate-950 ring-current" : ""
            )}
            id={`filter-severity-${s.key}`}
          >
            {s.label}: {summary[s.key] ?? 0}
          </button>
        ))}
        <button
          onClick={() => setShowResolved(!showResolved)}
          className={clsx(
            "px-3 py-1.5 rounded-lg border text-xs font-semibold transition-all ml-auto",
            showResolved
              ? "border-slate-500 text-slate-300 bg-slate-700"
              : "border-slate-700 text-slate-500 bg-slate-900"
          )}
          id="toggle-resolved"
        >
          {showResolved ? "Showing Resolved" : "Show Resolved"}
        </button>
      </div>

      {/* Alert List */}
      {isLoading ? (
        <div className="space-y-3">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="skeleton h-28 rounded-xl" />
          ))}
        </div>
      ) : alerts.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="text-3xl mb-3">✅</div>
          <div className="text-slate-300 font-medium">No alerts found</div>
          <div className="text-slate-500 text-sm mt-1">
            {showResolved ? "No resolved alerts." : "No active warnings at this time."}
          </div>
        </div>
      ) : (
        <div className="space-y-3">
          {alerts
            .sort((a, b) =>
              SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity)
            )
            .map((alert) => (
              <AlertCard key={alert.id} alert={alert} onResolve={handleResolve} />
            ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3">
          <button className="btn-secondary text-sm" onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1}>
            ← Prev
          </button>
          <span className="text-sm text-slate-400">Page {page} / {totalPages}</span>
          <button className="btn-secondary text-sm" onClick={() => setPage((p) => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
