"""
Pydantic v2 schemas for API request/response validation.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.orm import (
    AlertSeverity,
    AlertType,
    FileType,
    ImportStatus,
    ProjectStatus,
    RiskLevel,
    UserRole,
)


# ─── Auth ─────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    full_name: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    role: UserRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str = Field(min_length=8)
    role: UserRole = UserRole.viewer


# ─── Projects ─────────────────────────────────────────────────────────────────

class ProjectBase(BaseModel):
    project_id: str
    project_name: str
    ministry: Optional[str] = None
    department: Optional[str] = None
    implementing_agency: Optional[str] = None
    sector: Optional[str] = None
    state: Optional[str] = None
    original_cost: Optional[float] = None
    revised_cost: Optional[float] = None
    original_completion_date: Optional[date] = None
    revised_completion_date: Optional[date] = None
    current_status: ProjectStatus = ProjectStatus.unknown


class ProjectOut(ProjectBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListItem(BaseModel):
    id: uuid.UUID
    project_id: str
    project_name: str
    ministry: Optional[str] = None
    sector: Optional[str] = None
    state: Optional[str] = None
    current_status: ProjectStatus
    original_cost: Optional[float] = None
    revised_cost: Optional[float] = None
    # Latest snapshot fields (joined)
    physical_progress: Optional[float] = None
    cumulative_expenditure: Optional[float] = None
    report_month: Optional[date] = None
    # Latest risk
    overall_risk: Optional[RiskLevel] = None
    overall_health: Optional[float] = None

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectOut):
    snapshots: list[SnapshotOut] = []
    milestones: list[MilestoneOut] = []
    latest_risk: Optional[RiskAssessmentOut] = None
    active_alerts: list[AlertOut] = []


# ─── Snapshots ────────────────────────────────────────────────────────────────

class SnapshotOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    report_month: date
    physical_progress: Optional[float] = None
    planned_progress: Optional[float] = None
    cumulative_expenditure: Optional[float] = None
    current_cost: Optional[float] = None
    current_completion_date: Optional[date] = None
    current_status: Optional[ProjectStatus] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Milestones ───────────────────────────────────────────────────────────────

class MilestoneOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    milestone_name: str
    planned_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[str] = None

    model_config = {"from_attributes": True}


# ─── Risk ─────────────────────────────────────────────────────────────────────

class RiskAssessmentOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    snapshot_id: Optional[uuid.UUID] = None
    financial_health: Optional[float] = None
    schedule_health: Optional[float] = None
    progress_health: Optional[float] = None
    milestone_health: Optional[float] = None
    overall_health: Optional[float] = None
    overall_risk: RiskLevel
    financial_risk: RiskLevel
    schedule_risk: RiskLevel
    progress_risk: RiskLevel
    progress_gap: Optional[float] = None
    spending_progress_gap: Optional[float] = None
    cost_escalation_pct: Optional[float] = None
    schedule_escalation_days: Optional[int] = None
    time_consumed_pct: Optional[float] = None
    expenditure_pct: Optional[float] = None
    progress_velocity: Optional[float] = None
    ml_prediction_probability: Optional[float] = None
    ml_risk_class: Optional[str] = None
    explanation: Optional[list[str]] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Alerts ───────────────────────────────────────────────────────────────────

class AlertOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    project_name: Optional[str] = None
    alert_type: AlertType
    severity: AlertSeverity
    title: str
    description: str
    evidence: Optional[dict] = None
    recommended_action: Optional[str] = None
    is_resolved: bool
    report_month: Optional[date] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AlertResolve(BaseModel):
    resolution_note: str


# ─── Imports ──────────────────────────────────────────────────────────────────

class ImportOut(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    status: ImportStatus
    rows_found: int
    rows_processed: int
    rows_rejected: int
    duplicates: int
    new_projects: int
    updated_projects: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    error_details: Optional[Any] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    id: uuid.UUID
    filename: str
    file_type: FileType
    report_month: Optional[date] = None
    processing_status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ─── Analytics ────────────────────────────────────────────────────────────────

class PortfolioSummary(BaseModel):
    total_projects: int
    low_risk_count: int
    medium_risk_count: int
    high_risk_count: int
    critical_risk_count: int
    avg_health_score: Optional[float] = None
    total_original_cost: Optional[float] = None
    total_revised_cost: Optional[float] = None
    total_expenditure: Optional[float] = None
    stalled_count: int = 0


class SectorStat(BaseModel):
    sector: str
    project_count: int
    avg_health: Optional[float] = None
    high_risk_count: int
    total_cost: Optional[float] = None


class StateStat(BaseModel):
    state: str
    project_count: int
    avg_health: Optional[float] = None
    high_risk_count: int


class MinistryStats(BaseModel):
    ministry: str
    project_count: int
    avg_cost_escalation: Optional[float] = None
    high_risk_count: int


# ─── Forecasting ──────────────────────────────────────────────────────────────

class ForecastOut(BaseModel):
    project_id: uuid.UUID
    forecast_completion_date: Optional[date] = None
    forecast_progress_next_month: Optional[float] = None
    forecast_expenditure_next_month: Optional[float] = None
    expected_delay_days: Optional[int] = None
    method_used: str
    confidence_note: str


# ─── Pagination ───────────────────────────────────────────────────────────────

class PaginationMeta(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int


class PaginatedResponse(BaseModel):
    data: list
    pagination: PaginationMeta


# ─── Risk Config ──────────────────────────────────────────────────────────────

class RiskConfigOut(BaseModel):
    id: uuid.UUID
    name: str
    financial_weight: float
    schedule_weight: float
    progress_weight: float
    milestone_weight: float
    progress_gap_warning: float
    progress_gap_high: float
    spending_progress_gap_warning: float
    spending_progress_gap_high: float
    cost_escalation_warning_pct: float
    cost_escalation_high_pct: float
    schedule_delay_warning_days: int
    schedule_delay_high_days: int
    health_low_threshold: float
    health_medium_threshold: float
    health_critical_threshold: float

    model_config = {"from_attributes": True}


class RiskConfigUpdate(BaseModel):
    financial_weight: Optional[float] = None
    schedule_weight: Optional[float] = None
    progress_weight: Optional[float] = None
    milestone_weight: Optional[float] = None
    progress_gap_warning: Optional[float] = None
    progress_gap_high: Optional[float] = None
    spending_progress_gap_warning: Optional[float] = None
    spending_progress_gap_high: Optional[float] = None
    cost_escalation_warning_pct: Optional[float] = None
    cost_escalation_high_pct: Optional[float] = None
    schedule_delay_warning_days: Optional[int] = None
    schedule_delay_high_days: Optional[int] = None
    health_low_threshold: Optional[float] = None
    health_medium_threshold: Optional[float] = None
    health_critical_threshold: Optional[float] = None

    @field_validator("financial_weight", "schedule_weight", "progress_weight", "milestone_weight", mode="before")
    @classmethod
    def weight_range(cls, v):
        if v is not None and not (0.0 <= v <= 1.0):
            raise ValueError("Weights must be between 0.0 and 1.0")
        return v


# ─── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    database: str
    service: str
    version: str
