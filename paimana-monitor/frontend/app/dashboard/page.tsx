"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  getPortfolioSummary, getRiskDistribution, getSectorStats,
  getAlertsSummary, listAlerts, type PortfolioSummary, type Alert,
} from "@/lib/api";
import { formatCurrency, formatProgress, RISK_COLORS } from "@/lib/formatters";
import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer,
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
} from "recharts";

// ─── Stat Card ────────────────────────────────────────────────────────────────
function StatCard({
  label, value, sub, color = "text-slate-100", accent,
}: {
  label: string; value: string | number; sub?: string;
  color?: string; accent?: string;
}) {
  return (
    <div className={`card p-5 ${accent ? `border-l-2 border-l-[${accent}]` : ""}`}>
      <div className="stat-label">{label}</div>
      <div className={`text-2xl font-bold mt-1 ${color}`}>{value}</div>
      {sub && <div className="text-xs text-slate-500 mt-0.5">{sub}</div>}
    </div>
  );
}

// ─── Risk Distribution Pie ────────────────────────────────────────────────────
function RiskPie({ data }: { data: Record<string, number> }) {
  const chartData = [
    { name: "Low", value: data.low || 0, color: RISK_COLORS.low },
    { name: "Medium", value: data.medium || 0, color: RISK_COLORS.medium },
    { name: "High", value: data.high || 0, color: RISK_COLORS.high },
    { name: "Critical", value: data.critical || 0, color: RISK_COLORS.critical },
  ].filter((d) => d.value > 0);

  return (
    <div className="card p-5">
      <h3 className="text-sm font-semibold text-slate-300 mb-4">Risk Distribution</h3>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie data={chartData} cx="50%" cy="50%" innerRadius={55} outerRadius={80}
            paddingAngle={3} dataKey="value">
            {chartData.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
            labelStyle={{ color: "#94a3b8" }}
            itemStyle={{ color: "#f1f5f9" }}
          />
        </PieChart>
      </ResponsiveContainer>
      <div className="flex flex-wrap gap-2 justify-center mt-2">
        {chartData.map((d) => (
          <div key={d.name} className="flex items-center gap-1.5 text-xs text-slate-400">
            <span className="w-2.5 h-2.5 rounded-full" style={{ background: d.color }} />
            {d.name}: <span className="font-semibold text-slate-200">{d.value}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Alert Summary Panel ──────────────────────────────────────────────────────
function AlertPanel({ alerts }: { alerts: Alert[] }) {
  const severityOrder = ["critical", "high", "medium", "low"];
  const sorted = [...alerts].sort(
    (a, b) => severityOrder.indexOf(a.severity) - severityOrder.indexOf(b.severity)
  );

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-300">Recent Early Warnings</h3>
        <Link href="/dashboard/alerts" className="text-xs text-blue-400 hover:text-blue-300">
          View all →
        </Link>
      </div>
      <div className="space-y-2">
        {sorted.length === 0 ? (
          <div className="text-sm text-slate-500 py-4 text-center">No active warnings</div>
        ) : (
          sorted.slice(0, 6).map((alert) => (
            <div key={alert.id}
              className="flex items-start gap-3 p-3 bg-slate-900/60 rounded-lg border border-slate-800/50 hover:border-slate-700 transition-colors">
              <span className={`mt-0.5 w-2 h-2 rounded-full flex-shrink-0 ${
                alert.severity === "critical" ? "bg-purple-400" :
                alert.severity === "high" ? "bg-red-400" :
                alert.severity === "medium" ? "bg-amber-400" : "bg-blue-400"
              }`} />
              <div className="min-w-0">
                <div className="text-xs font-medium text-slate-300 truncate">{alert.project_name}</div>
                <div className="text-xs text-slate-500 truncate mt-0.5">{alert.description}</div>
              </div>
              <span className={`ml-auto text-[10px] font-semibold uppercase tracking-wider px-1.5 py-0.5 rounded flex-shrink-0 ${
                alert.severity === "critical" ? "bg-purple-500/20 text-purple-400" :
                alert.severity === "high" ? "bg-red-500/20 text-red-400" :
                alert.severity === "medium" ? "bg-amber-500/20 text-amber-400" : "bg-blue-500/20 text-blue-400"
              }`}>
                {alert.severity}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────
export default function DashboardPage() {
  const [summary, setSummary] = useState<PortfolioSummary | null>(null);
  const [riskDist, setRiskDist] = useState<Record<string, number>>({});
  const [sectorData, setSectorData] = useState<unknown[]>([]);
  const [recentAlerts, setRecentAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [sum, dist, sectors, alertsRes] = await Promise.all([
          getPortfolioSummary(),
          getRiskDistribution(),
          getSectorStats(),
          listAlerts({ limit: 10, is_resolved: false }),
        ]);
        setSummary(sum);
        setRiskDist(dist);
        setSectorData((sectors as Record<string, unknown>[]).slice(0, 8));
        setRecentAlerts(alertsRes.data);
      } catch (e) {
        console.error("Dashboard load error", e);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="skeleton h-8 w-64 rounded" />
        <div className="grid grid-cols-4 gap-4">
          {[...Array(4)].map((_, i) => <div key={i} className="skeleton h-28 rounded-xl" />)}
        </div>
        <div className="grid grid-cols-3 gap-4">
          {[...Array(3)].map((_, i) => <div key={i} className="skeleton h-64 rounded-xl" />)}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Portfolio Dashboard</h1>
          <p className="text-sm text-slate-500 mt-0.5">Infrastructure Project Monitoring · PAIMANA / OCMS</p>
        </div>
        <div className="text-xs text-slate-500 text-right">
          <div className="font-medium text-slate-400">SYNTHETIC DATA</div>
          <div>Development Mode · Not official PAIMANA data</div>
        </div>
      </div>

      {/* Primary KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Projects"
          value={summary?.total_projects ?? 0}
          sub="Portfolio-wide"
        />
        <StatCard
          label="At High/Critical Risk"
          value={(summary?.high_risk_count ?? 0) + (summary?.critical_risk_count ?? 0)}
          sub={`${summary?.critical_risk_count ?? 0} critical`}
          color="text-red-400"
        />
        <StatCard
          label="Active Warnings"
          value={summary?.active_alerts.total ?? 0}
          sub={`${summary?.active_alerts.critical ?? 0} critical`}
          color="text-amber-400"
        />
        <StatCard
          label="Stalled Projects"
          value={summary?.stalled_count ?? 0}
          sub="Needs attention"
          color="text-orange-400"
        />
      </div>

      {/* Financial KPIs */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        <StatCard
          label="Total Original Cost"
          value={formatCurrency(summary?.total_original_cost)}
          sub="At sanction"
        />
        <StatCard
          label="Total Revised Cost"
          value={formatCurrency(summary?.total_revised_cost)}
          sub="Current estimate"
          color={
            (summary?.total_revised_cost ?? 0) > (summary?.total_original_cost ?? 0)
              ? "text-amber-400" : "text-green-400"
          }
        />
        <StatCard
          label="Cumulative Expenditure"
          value={formatCurrency(summary?.total_expenditure)}
          sub="Incurred to date"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Risk Distribution Pie */}
        <RiskPie data={riskDist} />

        {/* Sector Bar Chart */}
        <div className="card p-5 md:col-span-2">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Projects by Sector</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={sectorData as Record<string, unknown>[]} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" tick={{ fill: "#64748b", fontSize: 11 }} />
              <YAxis type="category" dataKey="sector" width={80}
                tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <Tooltip
                contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
                itemStyle={{ color: "#f1f5f9" }}
              />
              <Bar dataKey="project_count" fill="#3b82f6" radius={[0, 4, 4, 0]} name="Projects" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Risk breakdown + Alerts */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Risk counts */}
        <div className="card p-5 space-y-3">
          <h3 className="text-sm font-semibold text-slate-300 mb-4">Risk Breakdown</h3>
          {[
            { label: "Critical Risk", count: summary?.critical_risk_count ?? 0, color: "bg-purple-500", textColor: "text-purple-400" },
            { label: "High Risk", count: summary?.high_risk_count ?? 0, color: "bg-red-500", textColor: "text-red-400" },
            { label: "Medium Risk", count: summary?.medium_risk_count ?? 0, color: "bg-amber-500", textColor: "text-amber-400" },
            { label: "Low Risk", count: summary?.low_risk_count ?? 0, color: "bg-green-500", textColor: "text-green-400" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-3">
              <span className={`w-2.5 h-2.5 rounded-full ${item.color}`} />
              <span className="text-sm text-slate-400 flex-1">{item.label}</span>
              <span className={`text-sm font-bold ${item.textColor}`}>{item.count}</span>
              <div className="w-24 h-1.5 bg-slate-800 rounded-full overflow-hidden">
                <div
                  className={`h-full ${item.color} rounded-full`}
                  style={{ width: `${summary?.total_projects ? (item.count / summary.total_projects) * 100 : 0}%` }}
                />
              </div>
            </div>
          ))}
          <div className="pt-2 border-t border-slate-800">
            <Link href="/dashboard/projects?risk=high" className="text-xs text-blue-400 hover:text-blue-300">
              View high-risk projects →
            </Link>
          </div>
        </div>

        {/* Alerts */}
        <div className="md:col-span-2">
          <AlertPanel alerts={recentAlerts} />
        </div>
      </div>
    </div>
  );
}
