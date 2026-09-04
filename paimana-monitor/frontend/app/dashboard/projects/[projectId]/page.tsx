"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import {
  getProject, getProjectForecast,
  type ProjectDetail, type Forecast,
} from "@/lib/api";
import {
  formatCurrency, formatProgress, formatDate, formatDays,
  RISK_COLORS,
} from "@/lib/formatters";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Legend, ReferenceLine,
} from "recharts";
import clsx from "clsx";

// ─── Risk Health Bar ──────────────────────────────────────────────────────────
function HealthBar({ label, score, risk }: { label: string; score?: number; risk: string }) {
  const color =
    risk === "critical" ? "bg-purple-500" :
    risk === "high" ? "bg-red-500" :
    risk === "medium" ? "bg-amber-500" : "bg-green-500";
  const textColor =
    risk === "critical" ? "text-purple-400" :
    risk === "high" ? "text-red-400" :
    risk === "medium" ? "text-amber-400" : "text-green-400";

  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="text-slate-400">{label}</span>
        <span className={clsx("font-semibold", textColor)}>
          {score != null ? score.toFixed(1) : "—"}
        </span>
      </div>
      <div className="progress-bar">
        <div className={clsx("progress-fill", color)} style={{ width: `${score ?? 0}%` }} />
      </div>
    </div>
  );
}

// ─── Progress Timeline Chart ──────────────────────────────────────────────────
function ProgressChart({ snapshots }: { snapshots: ProjectDetail["snapshots"] }) {
  const data = snapshots
    .slice()
    .sort((a, b) => a.report_month.localeCompare(b.report_month))
    .map((s) => ({
      month: s.report_month?.slice(0, 7) || "",
      actual: s.physical_progress != null ? +s.physical_progress.toFixed(1) : null,
      planned: s.planned_progress != null ? +s.planned_progress.toFixed(1) : null,
    }));

  if (data.length === 0) {
    return <div className="text-slate-500 text-sm py-8 text-center">No snapshot data available</div>;
  }

  return (
    <ResponsiveContainer width="100%" height={220}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey="month" tick={{ fill: "#64748b", fontSize: 11 }} />
        <YAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 11 }} unit="%" />
        <Tooltip
          contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
          itemStyle={{ color: "#f1f5f9" }}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
        <Line
          type="monotone" dataKey="actual" name="Actual Progress"
          stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} connectNulls
        />
        {data.some((d) => d.planned != null) && (
          <Line
            type="monotone" dataKey="planned" name="Planned Progress"
            stroke="#64748b" strokeWidth={1.5} strokeDasharray="5 5" dot={false} connectNulls
          />
        )}
        <ReferenceLine y={100} stroke="#22c55e" strokeDasharray="4 4" opacity={0.4} />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ─── Expenditure Chart ────────────────────────────────────────────────────────
function ExpenditureChart({ snapshots }: { snapshots: ProjectDetail["snapshots"] }) {
  const data = snapshots
    .slice()
    .sort((a, b) => a.report_month.localeCompare(b.report_month))
    .map((s) => ({
      month: s.report_month?.slice(0, 7) || "",
      expenditure: s.cumulative_expenditure != null
        ? +(+s.cumulative_expenditure / 100).toFixed(2) : null,
      cost: s.current_cost != null ? +(+s.current_cost / 100).toFixed(2) : null,
    }));

  if (data.length === 0) return null;

  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
        <XAxis dataKey="month" tick={{ fill: "#64748b", fontSize: 11 }} />
        <YAxis tick={{ fill: "#64748b", fontSize: 11 }} unit=" Cr" />
        <Tooltip
          contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
          itemStyle={{ color: "#f1f5f9" }}
          formatter={(v: number) => `₹ ${v} Cr`}
        />
        <Legend wrapperStyle={{ fontSize: 12, color: "#94a3b8" }} />
        <Line type="monotone" dataKey="expenditure" name="Cumulative Exp."
          stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} connectNulls />
        <Line type="monotone" dataKey="cost" name="Revised Cost"
          stroke="#f59e0b" strokeWidth={1.5} strokeDasharray="5 5" dot={false} connectNulls />
      </LineChart>
    </ResponsiveContainer>
  );
}

// ─── Forecast Panel ───────────────────────────────────────────────────────────
function ForecastPanel({ forecast }: { forecast: Forecast | null }) {
  if (!forecast || forecast.method_used === "insufficient_data") {
    return (
      <div className="card p-5">
        <h3 className="text-sm font-semibold text-slate-300 mb-3">Completion Forecast</h3>
        <div className="text-sm text-slate-500 py-4 text-center">
          Insufficient data for forecasting (min. 2 monthly observations required)
        </div>
      </div>
    );
  }

  const isDelayed = (forecast.expected_delay_days ?? 0) > 0;

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-300">Completion Forecast</h3>
        <span className="text-[10px] text-slate-500 uppercase tracking-wider bg-slate-800 px-2 py-0.5 rounded">
          {forecast.method_used.replace("_", " ")}
        </span>
      </div>
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <div className="stat-label">Forecast Date</div>
          <div className="text-lg font-bold text-slate-100 mt-1">
            {forecast.forecast_completion_date
              ? formatDate(forecast.forecast_completion_date)
              : "Cannot forecast"}
          </div>
        </div>
        <div>
          <div className="stat-label">Expected Delay</div>
          <div className={clsx(
            "text-lg font-bold mt-1",
            isDelayed ? "text-red-400" : "text-green-400"
          )}>
            {forecast.expected_delay_days != null
              ? (isDelayed
                ? `+${formatDays(forecast.expected_delay_days)} delay`
                : "On schedule")
              : "—"}
          </div>
        </div>
        <div>
          <div className="stat-label">Progress Next Month</div>
          <div className="text-lg font-bold text-blue-400 mt-1">
            {forecast.forecast_progress_next_month != null
              ? formatProgress(forecast.forecast_progress_next_month)
              : "—"}
          </div>
        </div>
        <div>
          <div className="stat-label">Expenditure Next Month</div>
          <div className="text-lg font-bold text-emerald-400 mt-1">
            {forecast.forecast_expenditure_next_month != null
              ? formatCurrency(forecast.forecast_expenditure_next_month)
              : "—"}
          </div>
        </div>
      </div>
      <div className="p-3 bg-slate-900/60 rounded-lg border border-slate-700/40 text-xs text-slate-500">
        ⚠ {forecast.confidence_note}
      </div>
    </div>
  );
}

// ─── Main Detail Page ─────────────────────────────────────────────────────────
export default function ProjectDetailPage() {
  const params = useParams();
  const projectId = params?.projectId as string;

  const [project, setProject] = useState<ProjectDetail | null>(null);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [tab, setTab] = useState<"overview" | "timeline" | "risk" | "milestones">("overview");

  useEffect(() => {
    if (!projectId) return;
    const load = async () => {
      try {
        const [p, f] = await Promise.all([
          getProject(projectId),
          getProjectForecast(projectId).catch(() => null),
        ]);
        setProject(p);
        setForecast(f);
      } catch (e) {
        console.error(e);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [projectId]);

  if (isLoading) {
    return (
      <div className="space-y-4 max-w-5xl mx-auto">
        <div className="skeleton h-8 w-96 rounded" />
        <div className="skeleton h-48 rounded-xl" />
        <div className="grid grid-cols-2 gap-4">
          <div className="skeleton h-64 rounded-xl" />
          <div className="skeleton h-64 rounded-xl" />
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="text-center py-20">
        <div className="text-slate-500">Project not found</div>
        <Link href="/dashboard/projects" className="text-blue-400 text-sm mt-2 block">← Back to projects</Link>
      </div>
    );
  }

  const ra = project.latest_risk;
  const overallRisk = ra?.overall_risk || "unknown";
  const riskColor =
    overallRisk === "critical" ? "text-purple-400" :
    overallRisk === "high" ? "text-red-400" :
    overallRisk === "medium" ? "text-amber-400" : "text-green-400";

  return (
    <div className="space-y-5 max-w-6xl mx-auto animate-fade-in">
      {/* Breadcrumb */}
      <div className="flex items-center gap-2 text-sm text-slate-500">
        <Link href="/dashboard/projects" className="hover:text-slate-300 transition-colors">Projects</Link>
        <span>/</span>
        <span className="text-slate-300">{project.project_name}</span>
      </div>

      {/* Header */}
      <div className="card p-6">
        <div className="flex items-start justify-between gap-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-3 flex-wrap">
              <span className="font-mono text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded">
                {project.project_id}
              </span>
              <span className={clsx(
                "text-xs px-2 py-0.5 rounded-full font-semibold uppercase tracking-wide",
                overallRisk === "critical" ? "bg-purple-500/20 text-purple-400 border border-purple-500/20" :
                overallRisk === "high" ? "bg-red-500/20 text-red-400 border border-red-500/20" :
                overallRisk === "medium" ? "bg-amber-500/20 text-amber-400 border border-amber-500/20" :
                "bg-green-500/20 text-green-400 border border-green-500/20"
              )}>
                {overallRisk} risk
              </span>
            </div>
            <h1 className="text-xl font-bold text-slate-100 mt-2 leading-snug">
              {project.project_name}
            </h1>
            <div className="flex flex-wrap gap-4 mt-3 text-sm text-slate-400">
              {project.ministry && <span>🏛 {project.ministry}</span>}
              {project.sector && <span>🔧 {project.sector}</span>}
              {project.state && <span>📍 {project.state}</span>}
              {project.implementing_agency && <span>🏢 {project.implementing_agency}</span>}
            </div>
          </div>
          {ra?.overall_health != null && (
            <div className="text-right flex-shrink-0">
              <div className="stat-label">Health Score</div>
              <div className={clsx("text-4xl font-bold mt-1", riskColor)}>
                {ra.overall_health.toFixed(0)}
              </div>
              <div className="text-xs text-slate-600">/ 100</div>
            </div>
          )}
        </div>

        {/* Quick KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-5 pt-5 border-t border-slate-800">
          <div>
            <div className="stat-label">Physical Progress</div>
            <div className="text-xl font-bold text-blue-400 mt-1">
              {formatProgress(project.snapshots[project.snapshots.length - 1]?.physical_progress)}
            </div>
          </div>
          <div>
            <div className="stat-label">Original Cost</div>
            <div className="text-xl font-bold mt-1">{formatCurrency(project.original_cost)}</div>
          </div>
          <div>
            <div className="stat-label">Revised Cost</div>
            <div className={clsx(
              "text-xl font-bold mt-1",
              (project.revised_cost ?? 0) > (project.original_cost ?? 0) ? "text-amber-400" : "text-slate-100"
            )}>
              {formatCurrency(project.revised_cost)}
            </div>
          </div>
          <div>
            <div className="stat-label">Original Completion</div>
            <div className="text-xl font-bold mt-1">{formatDate(project.original_completion_date)}</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 border-b border-slate-800">
        {(["overview", "timeline", "risk", "milestones"] as const).map((t) => (
          <button
            key={t}
            id={`tab-${t}`}
            onClick={() => setTab(t)}
            className={clsx(
              "px-4 py-2.5 text-sm font-medium transition-colors capitalize border-b-2 -mb-px",
              tab === t
                ? "text-blue-400 border-blue-500"
                : "text-slate-500 border-transparent hover:text-slate-300"
            )}
          >
            {t === "risk" ? "Risk Analysis" : t}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {tab === "overview" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="space-y-5">
            {/* Progress Chart */}
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-slate-300 mb-4">Progress Over Time</h3>
              <ProgressChart snapshots={project.snapshots} />
            </div>
            {/* Expenditure Chart */}
            <div className="card p-5">
              <h3 className="text-sm font-semibold text-slate-300 mb-4">Expenditure Trajectory</h3>
              <ExpenditureChart snapshots={project.snapshots} />
            </div>
          </div>
          <div className="space-y-5">
            <ForecastPanel forecast={forecast} />
            {/* Active Alerts */}
            {project.active_alerts.length > 0 && (
              <div className="card p-5">
                <h3 className="text-sm font-semibold text-slate-300 mb-3">
                  Active Warnings ({project.active_alerts.length})
                </h3>
                <div className="space-y-2">
                  {project.active_alerts.map((alert) => (
                    <div key={alert.id} className="p-3 bg-slate-900/60 rounded-lg border border-slate-800 text-sm">
                      <div className="flex items-center gap-2 mb-1">
                        <span className={clsx(
                          "text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded",
                          alert.severity === "critical" ? "bg-purple-500/20 text-purple-400" :
                          alert.severity === "high" ? "bg-red-500/20 text-red-400" :
                          "bg-amber-500/20 text-amber-400"
                        )}>
                          {alert.severity}
                        </span>
                        <span className="text-slate-300 font-medium">{alert.alert_type.replace(/_/g, " ")}</span>
                      </div>
                      <p className="text-slate-400 text-xs">{alert.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {tab === "timeline" && (
        <div className="card p-5 overflow-x-auto">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Monthly Snapshots</h3>
          <table className="data-table">
            <thead>
              <tr>
                <th>Month</th>
                <th>Physical Progress</th>
                <th>Planned Progress</th>
                <th>Gap</th>
                <th>Cumulative Exp.</th>
                <th>Current Cost</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {project.snapshots
                .slice()
                .sort((a, b) => b.report_month.localeCompare(a.report_month))
                .map((snap) => {
                  const gap =
                    snap.physical_progress != null && snap.planned_progress != null
                      ? snap.physical_progress - snap.planned_progress
                      : null;
                  return (
                    <tr key={snap.id}>
                      <td className="font-mono text-xs">{snap.report_month}</td>
                      <td className="text-blue-400 font-semibold">
                        {formatProgress(snap.physical_progress)}
                      </td>
                      <td className="text-slate-400">{formatProgress(snap.planned_progress)}</td>
                      <td className={clsx(
                        "font-semibold",
                        gap == null ? "text-slate-500" :
                        gap >= 0 ? "text-green-400" : "text-red-400"
                      )}>
                        {gap != null ? (gap >= 0 ? `+${gap.toFixed(1)}%` : `${gap.toFixed(1)}%`) : "—"}
                      </td>
                      <td>{formatCurrency(snap.cumulative_expenditure)}</td>
                      <td>{formatCurrency(snap.current_cost)}</td>
                      <td>
                        <span className="text-xs text-slate-400 capitalize">
                          {snap.current_status || "—"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
            </tbody>
          </table>
        </div>
      )}

      {tab === "risk" && ra && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Dimension Health Scores</h3>
            <div className="space-y-4">
              <HealthBar label="Financial Health" score={ra.financial_health ?? undefined} risk={ra.financial_risk} />
              <HealthBar label="Schedule Health" score={ra.schedule_health ?? undefined} risk={ra.schedule_risk} />
              <HealthBar label="Progress Health" score={ra.progress_health ?? undefined} risk={ra.progress_risk} />
              <HealthBar label="Milestone Health" score={ra.milestone_health ?? undefined} risk="low" />
            </div>
            <div className="mt-5 pt-4 border-t border-slate-800 grid grid-cols-2 gap-3 text-sm">
              {ra.cost_escalation_pct != null && (
                <div>
                  <div className="stat-label">Cost Escalation</div>
                  <div className={clsx("font-bold mt-0.5", ra.cost_escalation_pct > 10 ? "text-amber-400" : "text-slate-200")}>
                    +{ra.cost_escalation_pct.toFixed(1)}%
                  </div>
                </div>
              )}
              {ra.schedule_escalation_days != null && (
                <div>
                  <div className="stat-label">Schedule Delay</div>
                  <div className={clsx("font-bold mt-0.5", ra.schedule_escalation_days > 30 ? "text-red-400" : "text-slate-200")}>
                    {formatDays(ra.schedule_escalation_days)}
                  </div>
                </div>
              )}
              {ra.progress_gap != null && (
                <div>
                  <div className="stat-label">Progress Gap</div>
                  <div className={clsx("font-bold mt-0.5", ra.progress_gap < -10 ? "text-red-400" : "text-slate-200")}>
                    {ra.progress_gap > 0 ? `+${ra.progress_gap.toFixed(1)}` : ra.progress_gap.toFixed(1)}%
                  </div>
                </div>
              )}
              {ra.expenditure_pct != null && (
                <div>
                  <div className="stat-label">Expenditure %</div>
                  <div className="font-bold mt-0.5">{ra.expenditure_pct.toFixed(1)}%</div>
                </div>
              )}
            </div>
          </div>

          <div className="card p-5">
            <h3 className="text-sm font-semibold text-slate-300 mb-4">Risk Explanation</h3>
            <div className="space-y-2">
              {(ra.explanation || []).map((exp, i) => (
                <div key={i} className="flex gap-2 p-3 bg-slate-900/60 rounded-lg text-sm">
                  <span className="text-amber-400 mt-0.5 flex-shrink-0">•</span>
                  <span className="text-slate-300">{exp}</span>
                </div>
              ))}
              {(!ra.explanation || ra.explanation.length === 0) && (
                <div className="text-slate-500 text-sm py-4 text-center">
                  No specific risk factors detected
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {tab === "milestones" && (
        <div className="card p-5">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">
            Milestones ({project.milestones.length})
          </h3>
          {project.milestones.length === 0 ? (
            <div className="text-slate-500 text-sm py-8 text-center">No milestones recorded</div>
          ) : (
            <table className="data-table">
              <thead>
                <tr>
                  <th>Milestone</th>
                  <th>Planned Date</th>
                  <th>Actual Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {project.milestones.map((m) => (
                  <tr key={m.id}>
                    <td className="font-medium text-slate-200">{m.milestone_name}</td>
                    <td>{formatDate(m.planned_date)}</td>
                    <td>{formatDate(m.actual_date)}</td>
                    <td>
                      <span className={clsx(
                        "text-xs px-2 py-0.5 rounded-full font-semibold",
                        m.status === "completed" ? "bg-green-500/20 text-green-400" :
                        m.status === "missed" ? "bg-red-500/20 text-red-400" :
                        m.status === "delayed" ? "bg-amber-500/20 text-amber-400" :
                        "bg-slate-700 text-slate-400"
                      )}>
                        {m.status || "pending"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
}
