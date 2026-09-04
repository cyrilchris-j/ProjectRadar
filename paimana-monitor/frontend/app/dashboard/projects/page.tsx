"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import {
  listProjects, type ProjectListItem, type ProjectFilters,
} from "@/lib/api";
import {
  formatCurrency, formatProgress, formatDate,
  RISK_COLORS, STATUS_BG, STATUS_LABELS,
} from "@/lib/formatters";
import clsx from "clsx";

const SECTORS = ["Roads", "Railways", "Ports", "Power", "Petroleum", "Water", "Urban", "Industrial"];
const RISK_LEVELS = ["low", "medium", "high", "critical"];
const STATUSES = ["ongoing", "stalled", "completed", "not_started"];

function RiskBadge({ risk }: { risk?: string }) {
  if (!risk) return <span className="text-slate-600">—</span>;
  const classes: Record<string, string> = {
    low: "risk-low",
    medium: "risk-medium",
    high: "risk-high",
    critical: "risk-critical",
  };
  return (
    <span className={classes[risk] || "risk-badge bg-slate-700 text-slate-300"}>
      {risk}
    </span>
  );
}

function ProgressBar({ value, planned }: { value?: number; planned?: number }) {
  if (value == null) return <span className="text-slate-600">—</span>;
  const gap = planned != null ? value - planned : null;
  const color =
    gap == null ? "bg-blue-500" :
    gap >= 0 ? "bg-green-500" :
    gap >= -10 ? "bg-amber-500" : "bg-red-500";

  return (
    <div className="flex items-center gap-2">
      <div className="progress-bar w-20 flex-shrink-0">
        <div className={`progress-fill ${color}`} style={{ width: `${value}%` }} />
      </div>
      <span className="text-xs text-slate-300 font-medium">{value.toFixed(1)}%</span>
    </div>
  );
}

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectListItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(true);
  const [filters, setFilters] = useState<ProjectFilters>({ limit: 20 });

  const load = useCallback(async () => {
    setIsLoading(true);
    try {
      const res = await listProjects({ ...filters, page });
      setProjects(res.data);
      setTotal(res.pagination.total);
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  }, [filters, page]);

  useEffect(() => { load(); }, [load]);

  const totalPages = Math.max(1, Math.ceil(total / (filters.limit || 20)));

  const setFilter = (key: keyof ProjectFilters, value: string | undefined) => {
    setFilters((prev) => ({ ...prev, [key]: value || undefined }));
    setPage(1);
  };

  return (
    <div className="space-y-5 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-slate-100">Projects</h1>
          <p className="text-sm text-slate-500 mt-0.5">
            {total.toLocaleString()} projects in portfolio
          </p>
        </div>
        <Link href="/dashboard/import" className="btn-primary text-sm">
          + Import Data
        </Link>
      </div>

      {/* Filters */}
      <div className="card p-4 flex flex-wrap gap-3">
        <input
          className="input flex-1 min-w-48 text-sm"
          placeholder="Search by project name…"
          value={filters.search || ""}
          onChange={(e) => setFilter("search", e.target.value)}
          id="search-input"
        />
        <select
          className="select text-sm w-40"
          value={filters.risk || ""}
          onChange={(e) => setFilter("risk", e.target.value)}
          id="filter-risk"
        >
          <option value="">All Risk Levels</option>
          {RISK_LEVELS.map((r) => (
            <option key={r} value={r}>{r.charAt(0).toUpperCase() + r.slice(1)} Risk</option>
          ))}
        </select>
        <select
          className="select text-sm w-40"
          value={filters.sector || ""}
          onChange={(e) => setFilter("sector", e.target.value)}
          id="filter-sector"
        >
          <option value="">All Sectors</option>
          {SECTORS.map((s) => <option key={s} value={s}>{s}</option>)}
        </select>
        <select
          className="select text-sm w-40"
          value={filters.status || ""}
          onChange={(e) => setFilter("status", e.target.value)}
          id="filter-status"
        >
          <option value="">All Statuses</option>
          {STATUSES.map((s) => (
            <option key={s} value={s}>{STATUS_LABELS[s]}</option>
          ))}
        </select>
        <button
          className="btn-ghost text-sm"
          onClick={() => { setFilters({ limit: 20 }); setPage(1); }}
          id="clear-filters"
        >
          Clear filters
        </button>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="data-table">
            <thead>
              <tr>
                <th>Project ID</th>
                <th>Project Name</th>
                <th>Sector</th>
                <th>State</th>
                <th>Progress</th>
                <th>Revised Cost</th>
                <th>Expenditure</th>
                <th>Risk</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                [...Array(8)].map((_, i) => (
                  <tr key={i}>
                    {[...Array(9)].map((_, j) => (
                      <td key={j}><div className="skeleton h-4 rounded" /></td>
                    ))}
                  </tr>
                ))
              ) : projects.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center text-slate-500 py-12">
                    No projects match the current filters
                  </td>
                </tr>
              ) : (
                projects.map((project) => (
                  <tr
                    key={project.id}
                    onClick={() => window.location.href = `/dashboard/projects/${project.project_id}`}
                    className="cursor-pointer"
                  >
                    <td>
                      <span className="font-mono text-xs text-slate-400">{project.project_id}</span>
                    </td>
                    <td>
                      <div className="font-medium text-slate-200 max-w-xs truncate">
                        {project.project_name}
                      </div>
                      {project.ministry && (
                        <div className="text-xs text-slate-500 truncate">{project.ministry}</div>
                      )}
                    </td>
                    <td className="text-slate-400">{project.sector || "—"}</td>
                    <td className="text-slate-400">{project.state || "—"}</td>
                    <td>
                      <ProgressBar value={project.physical_progress ?? undefined} />
                    </td>
                    <td className="text-slate-300 font-medium">
                      {formatCurrency(project.revised_cost)}
                    </td>
                    <td className="text-slate-300">
                      {formatCurrency(project.cumulative_expenditure)}
                    </td>
                    <td>
                      <RiskBadge risk={project.overall_risk} />
                    </td>
                    <td>
                      <span className={clsx(
                        "text-xs px-2 py-0.5 rounded-full font-medium",
                        STATUS_BG[project.current_status] || "bg-slate-700 text-slate-400"
                      )}>
                        {STATUS_LABELS[project.current_status] || project.current_status}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between px-4 py-3 border-t border-slate-800">
          <span className="text-xs text-slate-500">
            Showing {((page - 1) * (filters.limit || 20)) + 1}–
            {Math.min(page * (filters.limit || 20), total)} of {total}
          </span>
          <div className="flex items-center gap-2">
            <button
              className="btn-secondary text-xs py-1.5 px-3"
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              disabled={page === 1}
              id="prev-page"
            >
              ← Prev
            </button>
            <span className="text-xs text-slate-400">
              Page {page} / {totalPages}
            </span>
            <button
              className="btn-secondary text-xs py-1.5 px-3"
              onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              id="next-page"
            >
              Next →
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
