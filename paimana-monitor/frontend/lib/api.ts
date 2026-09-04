/**
 * Typed API client — all frontend HTTP calls go through here.
 * Never makes direct database calls from the frontend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// ─── Auth ──────────────────────────────────────────────────────────────────

let _token: string | null = null;

export function setToken(token: string | null) {
  _token = token;
  if (typeof window !== "undefined") {
    if (token) localStorage.setItem("paimana_token", token);
    else localStorage.removeItem("paimana_token");
  }
}

export function getToken(): string | null {
  if (_token) return _token;
  if (typeof window !== "undefined") {
    return localStorage.getItem("paimana_token");
  }
  return null;
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  });

  if (res.status === 401) {
    setToken(null);
    if (typeof window !== "undefined") window.location.href = "/login";
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || "API error");
  }

  if (res.status === 204) return undefined as T;
  return res.json();
}

// ─── Auth endpoints ────────────────────────────────────────────────────────

export interface TokenResponse {
  access_token: string;
  token_type: string;
  role: string;
  full_name: string;
}

export interface CurrentUser {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const body = new URLSearchParams({ username: email, password });
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Login failed" }));
    throw new Error(error.detail || "Login failed");
  }
  return res.json();
}

export async function getMe(): Promise<CurrentUser> {
  return request<CurrentUser>("/api/auth/me");
}

// ─── Projects ──────────────────────────────────────────────────────────────

export interface ProjectListItem {
  id: string;
  project_id: string;
  project_name: string;
  ministry?: string;
  sector?: string;
  state?: string;
  current_status: string;
  original_cost?: number;
  revised_cost?: number;
  physical_progress?: number;
  cumulative_expenditure?: number;
  report_month?: string;
  overall_risk?: string;
  overall_health?: number;
}

export interface Snapshot {
  id: string;
  project_id: string;
  report_month: string;
  physical_progress?: number;
  planned_progress?: number;
  cumulative_expenditure?: number;
  current_cost?: number;
  current_completion_date?: string;
  current_status?: string;
  created_at: string;
}

export interface Milestone {
  id: string;
  project_id: string;
  milestone_name: string;
  planned_date?: string;
  actual_date?: string;
  status?: string;
}

export interface RiskAssessment {
  id: string;
  project_id: string;
  financial_health?: number;
  schedule_health?: number;
  progress_health?: number;
  milestone_health?: number;
  overall_health?: number;
  overall_risk: string;
  financial_risk: string;
  schedule_risk: string;
  progress_risk: string;
  progress_gap?: number;
  spending_progress_gap?: number;
  cost_escalation_pct?: number;
  schedule_escalation_days?: number;
  time_consumed_pct?: number;
  expenditure_pct?: number;
  progress_velocity?: number;
  explanation?: string[];
  created_at: string;
}

export interface Alert {
  id: string;
  project_id: string;
  project_name?: string;
  alert_type: string;
  severity: string;
  title: string;
  description: string;
  evidence?: Record<string, unknown>;
  recommended_action?: string;
  is_resolved: boolean;
  report_month?: string;
  created_at: string;
}

export interface ProjectDetail {
  id: string;
  project_id: string;
  project_name: string;
  ministry?: string;
  department?: string;
  implementing_agency?: string;
  sector?: string;
  state?: string;
  current_status: string;
  original_cost?: number;
  revised_cost?: number;
  original_completion_date?: string;
  revised_completion_date?: string;
  original_start_date?: string;
  snapshots: Snapshot[];
  milestones: Milestone[];
  latest_risk?: RiskAssessment;
  active_alerts: Alert[];
  created_at: string;
  updated_at: string;
}

export interface Forecast {
  project_id: string;
  forecast_completion_date?: string;
  forecast_progress_next_month?: number;
  forecast_expenditure_next_month?: number;
  expected_delay_days?: number;
  method_used: string;
  confidence_note: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  pagination: { page: number; limit: number; total: number; total_pages: number };
}

export interface ProjectFilters {
  page?: number;
  limit?: number;
  sector?: string;
  state?: string;
  ministry?: string;
  risk?: string;
  status?: string;
  search?: string;
}

export async function listProjects(
  filters: ProjectFilters = {}
): Promise<PaginatedResponse<ProjectListItem>> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== undefined && v !== "") params.set(k, String(v));
  });
  return request<PaginatedResponse<ProjectListItem>>(`/api/projects?${params}`);
}

export async function getProject(projectId: string): Promise<ProjectDetail> {
  return request<ProjectDetail>(`/api/projects/${projectId}`);
}

export async function getProjectHistory(projectId: string): Promise<Snapshot[]> {
  return request<Snapshot[]>(`/api/projects/${projectId}/history`);
}

export async function getProjectForecast(projectId: string): Promise<Forecast> {
  return request<Forecast>(`/api/projects/${projectId}/forecast`);
}

export async function getProjectRisk(projectId: string): Promise<RiskAssessment> {
  return request<RiskAssessment>(`/api/projects/${projectId}/risk`);
}

// ─── Analytics ─────────────────────────────────────────────────────────────

export interface PortfolioSummary {
  total_projects: number;
  low_risk_count: number;
  medium_risk_count: number;
  high_risk_count: number;
  critical_risk_count: number;
  avg_health_score?: number;
  total_original_cost?: number;
  total_revised_cost?: number;
  total_expenditure?: number;
  stalled_count: number;
  active_alerts: {
    total: number;
    critical: number;
    high: number;
    medium: number;
  };
}

export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  return request<PortfolioSummary>("/api/analytics/portfolio");
}

export async function getSectorStats(): Promise<unknown[]> {
  return request<unknown[]>("/api/analytics/sectors");
}

export async function getStateStats(): Promise<unknown[]> {
  return request<unknown[]>("/api/analytics/states");
}

export async function getRiskDistribution(): Promise<Record<string, number>> {
  return request<Record<string, number>>("/api/analytics/risk-distribution");
}

// ─── Alerts ────────────────────────────────────────────────────────────────

export interface AlertFilters {
  page?: number;
  limit?: number;
  severity?: string;
  alert_type?: string;
  is_resolved?: boolean;
}

export async function listAlerts(
  filters: AlertFilters = {}
): Promise<PaginatedResponse<Alert>> {
  const params = new URLSearchParams();
  Object.entries(filters).forEach(([k, v]) => {
    if (v !== undefined) params.set(k, String(v));
  });
  return request<PaginatedResponse<Alert>>(`/api/alerts?${params}`);
}

export async function getAlertsSummary(): Promise<Record<string, number>> {
  return request<Record<string, number>>("/api/alerts/summary");
}

export async function resolveAlert(
  alertId: string,
  resolution_note: string
): Promise<void> {
  return request(`/api/alerts/${alertId}/resolve`, {
    method: "PATCH",
    body: JSON.stringify({ resolution_note }),
  });
}

// ─── Imports ───────────────────────────────────────────────────────────────

export interface ImportRecord {
  id: string;
  document_id: string;
  status: string;
  rows_found: number;
  rows_processed: number;
  rows_rejected: number;
  duplicates: number;
  new_projects: number;
  updated_projects: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  error_details?: unknown;
  created_at: string;
}

export async function uploadFile(
  file: File,
  reportMonth?: string
): Promise<ImportRecord> {
  const formData = new FormData();
  formData.append("file", file);
  if (reportMonth) formData.append("report_month_str", reportMonth);

  const token = getToken();
  const headers: Record<string, string> = {};
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}/api/imports`, {
    method: "POST",
    headers,
    body: formData,
  });
  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(error.detail || "Upload failed");
  }
  return res.json();
}

export async function getImportStatus(importId: string): Promise<ImportRecord> {
  return request<ImportRecord>(`/api/imports/${importId}`);
}

export async function listImports(): Promise<ImportRecord[]> {
  return request<ImportRecord[]>("/api/imports");
}

// ─── Admin ─────────────────────────────────────────────────────────────────

export interface RiskConfig {
  id: string;
  name: string;
  financial_weight: number;
  schedule_weight: number;
  progress_weight: number;
  milestone_weight: number;
  progress_gap_warning: number;
  progress_gap_high: number;
  spending_progress_gap_warning: number;
  spending_progress_gap_high: number;
  cost_escalation_warning_pct: number;
  cost_escalation_high_pct: number;
  schedule_delay_warning_days: number;
  schedule_delay_high_days: number;
  health_low_threshold: number;
  health_medium_threshold: number;
  health_critical_threshold: number;
}

export async function getRiskConfig(): Promise<RiskConfig> {
  return request<RiskConfig>("/api/admin/risk-config");
}

export async function updateRiskConfig(
  updates: Partial<Omit<RiskConfig, "id" | "name">>
): Promise<RiskConfig> {
  return request<RiskConfig>("/api/admin/risk-config", {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
}

export async function listUsers(): Promise<unknown[]> {
  return request<unknown[]>("/api/admin/users");
}

export async function getAuditLogs(page = 1): Promise<unknown[]> {
  return request<unknown[]>(`/api/admin/audit-logs?page=${page}`);
}

// ─── Health ────────────────────────────────────────────────────────────────

export async function checkHealth(): Promise<{ status: string; database: string }> {
  return request("/health");
}
