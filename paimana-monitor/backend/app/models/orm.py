"""
SQLAlchemy ORM Models — mirrors the PostgreSQL schema exactly.
"""
import enum
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    BigInteger,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.connection import Base


# ─── Enums ───────────────────────────────────────────────────────────────────

class UserRole(str, enum.Enum):
    admin = "admin"
    analyst = "analyst"
    officer = "officer"
    viewer = "viewer"


class ProjectStatus(str, enum.Enum):
    ongoing = "ongoing"
    completed = "completed"
    stalled = "stalled"
    abandoned = "abandoned"
    not_started = "not_started"
    unknown = "unknown"


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AlertType(str, enum.Enum):
    schedule_delay = "schedule_delay"
    cost_overrun = "cost_overrun"
    progress_lag = "progress_lag"
    milestone_missed = "milestone_missed"
    expenditure_anomaly = "expenditure_anomaly"
    stalled_project = "stalled_project"
    data_quality = "data_quality"


class ImportStatus(str, enum.Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    partial = "partial"


class FileType(str, enum.Enum):
    pdf = "pdf"
    excel = "excel"
    csv = "csv"


class ProcessingStatus(str, enum.Enum):
    uploaded = "uploaded"
    queued = "queued"
    processing = "processing"
    processed = "processed"
    failed = "failed"


# ─── Models ──────────────────────────────────────────────────────────────────

class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    code: Mapped[Optional[str]] = mapped_column(String(50), unique=True)
    organization_type: Mapped[Optional[str]] = mapped_column(String(100))
    parent_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    password_hash: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False, default=UserRole.viewer)
    organization_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("organizations.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    project_name: Mapped[str] = mapped_column(Text, nullable=False)
    ministry: Mapped[Optional[str]] = mapped_column(Text)
    department: Mapped[Optional[str]] = mapped_column(Text)
    implementing_agency: Mapped[Optional[str]] = mapped_column(Text)
    sector: Mapped[Optional[str]] = mapped_column(String(100))
    sub_sector: Mapped[Optional[str]] = mapped_column(String(100))
    state: Mapped[Optional[str]] = mapped_column(String(100))
    district: Mapped[Optional[str]] = mapped_column(String(100))
    original_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(10), default="INR")
    original_start_date: Mapped[Optional[date]] = mapped_column(Date)
    original_completion_date: Mapped[Optional[date]] = mapped_column(Date)
    revised_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    revised_completion_date: Mapped[Optional[date]] = mapped_column(Date)
    current_status: Mapped[ProjectStatus] = mapped_column(Enum(ProjectStatus, name="project_status"), default=ProjectStatus.unknown)
    is_central_sector: Mapped[bool] = mapped_column(Boolean, default=False)
    project_category: Mapped[Optional[str]] = mapped_column(String(100))
    project_length_km: Mapped[Optional[float]] = mapped_column(Numeric(10, 2))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    snapshots: Mapped[list["ProjectSnapshot"]] = relationship("ProjectSnapshot", back_populates="project", order_by="ProjectSnapshot.report_month")
    risk_assessments: Mapped[list["RiskAssessment"]] = relationship("RiskAssessment", back_populates="project")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="project")
    milestones: Mapped[list["Milestone"]] = relationship("Milestone", back_populates="project")


class ProjectSnapshot(Base):
    __tablename__ = "project_snapshots"
    __table_args__ = (UniqueConstraint("project_id", "report_month"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    report_month: Mapped[date] = mapped_column(Date, nullable=False)
    physical_progress: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    planned_progress: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    cumulative_expenditure: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    current_cost: Mapped[Optional[float]] = mapped_column(Numeric(18, 2))
    current_completion_date: Mapped[Optional[date]] = mapped_column(Date)
    current_status: Mapped[Optional[ProjectStatus]] = mapped_column(Enum(ProjectStatus, name="project_status"))
    raw_progress_value: Mapped[Optional[str]] = mapped_column(Text)
    raw_expenditure_value: Mapped[Optional[str]] = mapped_column(Text)
    raw_cost_value: Mapped[Optional[str]] = mapped_column(Text)
    source_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="snapshots")


class Milestone(Base):
    __tablename__ = "milestones"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    milestone_name: Mapped[str] = mapped_column(Text, nullable=False)
    planned_date: Mapped[Optional[date]] = mapped_column(Date)
    actual_date: Mapped[Optional[date]] = mapped_column(Date)
    status: Mapped[Optional[str]] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="milestones")


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    filename: Mapped[str] = mapped_column(Text, nullable=False)
    file_type: Mapped[FileType] = mapped_column(Enum(FileType, name="file_type"), nullable=False)
    storage_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64))
    report_month: Mapped[Optional[date]] = mapped_column(Date)
    processing_status: Mapped[ProcessingStatus] = mapped_column(Enum(ProcessingStatus, name="processing_status"), default=ProcessingStatus.uploaded)
    uploaded_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    imports: Mapped[list["Import"]] = relationship("Import", back_populates="document")


class Import(Base):
    __tablename__ = "imports"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus, name="import_status"), default=ImportStatus.pending)
    rows_found: Mapped[int] = mapped_column(Integer, default=0)
    rows_processed: Mapped[int] = mapped_column(Integer, default=0)
    rows_rejected: Mapped[int] = mapped_column(Integer, default=0)
    duplicates: Mapped[int] = mapped_column(Integer, default=0)
    new_projects: Mapped[int] = mapped_column(Integer, default=0)
    updated_projects: Mapped[int] = mapped_column(Integer, default=0)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[dict]] = mapped_column(JSON)
    triggered_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    document: Mapped["Document"] = relationship("Document", back_populates="imports")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    snapshot_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("project_snapshots.id"))
    financial_health: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    schedule_health: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    progress_health: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    milestone_health: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    overall_health: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    overall_risk: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel, name="risk_level"), default=RiskLevel.low)
    financial_risk: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel, name="risk_level"), default=RiskLevel.low)
    schedule_risk: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel, name="risk_level"), default=RiskLevel.low)
    progress_risk: Mapped[RiskLevel] = mapped_column(Enum(RiskLevel, name="risk_level"), default=RiskLevel.low)
    progress_gap: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    spending_progress_gap: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    cost_escalation_pct: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    schedule_escalation_days: Mapped[Optional[int]] = mapped_column(Integer)
    time_consumed_pct: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    expenditure_pct: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    progress_velocity: Mapped[Optional[float]] = mapped_column(Numeric(6, 2))
    ml_prediction_probability: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    ml_risk_class: Mapped[Optional[str]] = mapped_column(String(50))
    explanation: Mapped[Optional[list]] = mapped_column(JSON)
    config_snapshot: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="risk_assessments")


class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=False)
    risk_assessment_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("risk_assessments.id"))
    alert_type: Mapped[AlertType] = mapped_column(Enum(AlertType, name="alert_type"), nullable=False)
    severity: Mapped[AlertSeverity] = mapped_column(Enum(AlertSeverity, name="alert_severity"), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[Optional[dict]] = mapped_column(JSON)
    recommended_action: Mapped[Optional[str]] = mapped_column(Text)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    resolution_note: Mapped[Optional[str]] = mapped_column(Text)
    report_month: Mapped[Optional[date]] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    project: Mapped["Project"] = relationship("Project", back_populates="alerts")


class RiskConfiguration(Base):
    __tablename__ = "risk_configurations"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, default="default")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    financial_weight: Mapped[float] = mapped_column(Numeric(4, 3), default=0.250)
    schedule_weight: Mapped[float] = mapped_column(Numeric(4, 3), default=0.300)
    progress_weight: Mapped[float] = mapped_column(Numeric(4, 3), default=0.250)
    milestone_weight: Mapped[float] = mapped_column(Numeric(4, 3), default=0.200)
    progress_gap_warning: Mapped[float] = mapped_column(Numeric(5, 2), default=-10.0)
    progress_gap_high: Mapped[float] = mapped_column(Numeric(5, 2), default=-20.0)
    spending_progress_gap_warning: Mapped[float] = mapped_column(Numeric(5, 2), default=10.0)
    spending_progress_gap_high: Mapped[float] = mapped_column(Numeric(5, 2), default=25.0)
    cost_escalation_warning_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=10.0)
    cost_escalation_high_pct: Mapped[float] = mapped_column(Numeric(5, 2), default=25.0)
    schedule_delay_warning_days: Mapped[int] = mapped_column(Integer, default=30)
    schedule_delay_high_days: Mapped[int] = mapped_column(Integer, default=90)
    health_low_threshold: Mapped[float] = mapped_column(Numeric(5, 2), default=75.0)
    health_medium_threshold: Mapped[float] = mapped_column(Numeric(5, 2), default=55.0)
    health_critical_threshold: Mapped[float] = mapped_column(Numeric(5, 2), default=35.0)
    updated_by: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(Text, nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(100))
    entity_id: Mapped[Optional[str]] = mapped_column(String(255))
    metadata_: Mapped[Optional[dict]] = mapped_column("metadata", JSON)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    algorithm: Mapped[str] = mapped_column(Text, nullable=False)
    features: Mapped[Optional[list]] = mapped_column(JSON)
    training_period: Mapped[Optional[str]] = mapped_column(Text)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)
    model_path: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
