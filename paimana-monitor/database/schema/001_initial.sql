-- =============================================================================
-- PAIMANA Project Intelligence & Early Warning System
-- Database Schema — Migration 001 (Initial)
-- Ministry of Statistics and Programme Implementation (MoSPI)
-- =============================================================================

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- for fuzzy text search on project names

-- =============================================================================
-- ENUM TYPES
-- =============================================================================

CREATE TYPE user_role AS ENUM ('admin', 'analyst', 'officer', 'viewer');
CREATE TYPE project_status AS ENUM (
    'ongoing', 'completed', 'stalled', 'abandoned', 'not_started', 'unknown'
);
CREATE TYPE risk_level AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_severity AS ENUM ('low', 'medium', 'high', 'critical');
CREATE TYPE alert_type AS ENUM (
    'schedule_delay', 'cost_overrun', 'progress_lag', 'milestone_missed',
    'expenditure_anomaly', 'stalled_project', 'data_quality'
);
CREATE TYPE import_status AS ENUM (
    'pending', 'processing', 'completed', 'failed', 'partial'
);
CREATE TYPE file_type AS ENUM ('pdf', 'excel', 'csv');
CREATE TYPE processing_status AS ENUM (
    'uploaded', 'queued', 'processing', 'processed', 'failed'
);

-- =============================================================================
-- ORGANIZATIONS
-- =============================================================================

CREATE TABLE organizations (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            TEXT NOT NULL,
    code            TEXT UNIQUE,
    organization_type TEXT,                 -- Ministry, Department, Agency, etc.
    parent_id       UUID REFERENCES organizations(id),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_organizations_code ON organizations(code);
CREATE INDEX idx_organizations_name ON organizations USING gin(name gin_trgm_ops);

-- =============================================================================
-- USERS
-- =============================================================================

CREATE TABLE users (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email           TEXT NOT NULL UNIQUE,
    full_name       TEXT NOT NULL,
    password_hash   TEXT NOT NULL,
    role            user_role NOT NULL DEFAULT 'viewer',
    organization_id UUID REFERENCES organizations(id),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    last_login_at   TIMESTAMPTZ,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);

-- =============================================================================
-- PROJECTS
-- =============================================================================
-- Master project record — one row per physical project.
-- Never overwrite historical values here; use project_snapshots for time-series.

CREATE TABLE projects (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    -- Source identifier from PAIMANA/OCMS
    project_id                  TEXT NOT NULL UNIQUE,   -- e.g. "705728"
    project_name                TEXT NOT NULL,

    -- Classification
    ministry                    TEXT,
    department                  TEXT,
    implementing_agency         TEXT,
    sector                      TEXT,                   -- Roads, Railways, etc.
    sub_sector                  TEXT,
    state                       TEXT,
    district                    TEXT,

    -- Financial (at project registration)
    original_cost               NUMERIC(18, 2),         -- ₹ Lakhs
    currency                    TEXT DEFAULT 'INR',

    -- Schedule (at project registration)
    original_start_date         DATE,
    original_completion_date    DATE,

    -- Current recorded values (latest known; always update with new snapshot)
    revised_cost                NUMERIC(18, 2),
    revised_completion_date     DATE,
    current_status              project_status DEFAULT 'unknown',

    -- Metadata
    is_central_sector           BOOLEAN DEFAULT FALSE,
    project_category            TEXT,
    project_length_km           NUMERIC(10, 2),         -- for linear infrastructure

    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_projects_project_id ON projects(project_id);
CREATE INDEX idx_projects_sector ON projects(sector);
CREATE INDEX idx_projects_state ON projects(state);
CREATE INDEX idx_projects_ministry ON projects(ministry);
CREATE INDEX idx_projects_status ON projects(current_status);
CREATE INDEX idx_projects_name ON projects USING gin(project_name gin_trgm_ops);

-- =============================================================================
-- PROJECT SNAPSHOTS
-- =============================================================================
-- One row per project per reporting period.
-- THIS IS THE CORE TIME-SERIES TABLE.
-- Never delete or overwrite historical snapshots.

CREATE TABLE project_snapshots (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id              UUID NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,

    -- Reporting period
    report_month            DATE NOT NULL,              -- First day of month: 2026-04-01

    -- Progress
    physical_progress       NUMERIC(5, 2),              -- 0.00–100.00 %
    planned_progress        NUMERIC(5, 2),              -- Derived or provided

    -- Financial
    cumulative_expenditure  NUMERIC(18, 2),             -- ₹ Lakhs
    current_cost            NUMERIC(18, 2),             -- Revised cost at this snapshot

    -- Schedule
    current_completion_date DATE,
    current_status          project_status,

    -- Raw source values (preserved for traceability, before normalization)
    raw_progress_value      TEXT,
    raw_expenditure_value   TEXT,
    raw_cost_value          TEXT,

    -- Source traceability
    source_document_id      UUID,                       -- FK to documents (set after insert)

    created_at              TIMESTAMPTZ DEFAULT NOW(),

    -- Enforce one snapshot per project per reporting period
    UNIQUE (project_id, report_month)
);

CREATE INDEX idx_snapshots_project_id ON project_snapshots(project_id);
CREATE INDEX idx_snapshots_report_month ON project_snapshots(report_month);
CREATE INDEX idx_snapshots_project_month ON project_snapshots(project_id, report_month DESC);

-- =============================================================================
-- MILESTONES
-- =============================================================================

CREATE TABLE milestones (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,
    milestone_name  TEXT NOT NULL,
    planned_date    DATE,
    actual_date     DATE,
    status          TEXT,           -- pending | completed | delayed | missed
    delay_days      INTEGER         -- computed: actual_date - planned_date
                        GENERATED ALWAYS AS (
                            CASE
                                WHEN actual_date IS NOT NULL AND planned_date IS NOT NULL
                                THEN (actual_date - planned_date)
                                ELSE NULL
                            END
                        ) STORED,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_milestones_project_id ON milestones(project_id);
CREATE INDEX idx_milestones_status ON milestones(status);

-- =============================================================================
-- DOCUMENTS (uploaded files)
-- =============================================================================

CREATE TABLE documents (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename            TEXT NOT NULL,
    file_type           file_type NOT NULL,
    storage_path        TEXT NOT NULL,
    file_size_bytes     BIGINT,
    file_hash           TEXT,                       -- SHA-256 for deduplication
    report_month        DATE,                       -- The reporting period the file covers
    processing_status   processing_status DEFAULT 'uploaded',
    uploaded_by         UUID REFERENCES users(id),
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_documents_file_hash ON documents(file_hash) WHERE file_hash IS NOT NULL;
CREATE INDEX idx_documents_report_month ON documents(report_month);

-- =============================================================================
-- IMPORTS (pipeline runs)
-- =============================================================================

CREATE TABLE imports (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id     UUID NOT NULL REFERENCES documents(id),
    status          import_status DEFAULT 'pending',
    rows_found      INTEGER DEFAULT 0,
    rows_processed  INTEGER DEFAULT 0,
    rows_rejected   INTEGER DEFAULT 0,
    duplicates      INTEGER DEFAULT 0,
    new_projects    INTEGER DEFAULT 0,
    updated_projects INTEGER DEFAULT 0,
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    error_message   TEXT,
    error_details   JSONB,          -- rejected rows and reasons
    triggered_by    UUID REFERENCES users(id),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_imports_document_id ON imports(document_id);
CREATE INDEX idx_imports_status ON imports(status);

-- =============================================================================
-- RISK ASSESSMENTS
-- =============================================================================

CREATE TABLE risk_assessments (
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id              UUID NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,
    snapshot_id             UUID REFERENCES project_snapshots(id),

    -- Dimension scores (0–100, higher = healthier)
    financial_health        NUMERIC(5, 2),
    schedule_health         NUMERIC(5, 2),
    progress_health         NUMERIC(5, 2),
    milestone_health        NUMERIC(5, 2),
    overall_health          NUMERIC(5, 2),

    -- Risk classification
    overall_risk            risk_level DEFAULT 'low',
    financial_risk          risk_level DEFAULT 'low',
    schedule_risk           risk_level DEFAULT 'low',
    progress_risk           risk_level DEFAULT 'low',

    -- Computed features (stored for audit / ML reuse)
    progress_gap            NUMERIC(6, 2),   -- actual - planned progress
    spending_progress_gap   NUMERIC(6, 2),   -- expenditure% - physical_progress%
    cost_escalation_pct     NUMERIC(6, 2),   -- (revised-original)/original * 100
    schedule_escalation_days INTEGER,
    time_consumed_pct       NUMERIC(5, 2),
    expenditure_pct         NUMERIC(5, 2),
    progress_velocity       NUMERIC(6, 2),   -- month-on-month progress delta

    -- ML output (optional)
    ml_prediction_probability NUMERIC(5, 4),
    ml_risk_class           TEXT,

    -- Explanation (JSON array of reason strings)
    explanation             JSONB,

    -- Configuration snapshot (weights used at time of calculation)
    config_snapshot         JSONB,

    created_at              TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_risk_project_id ON risk_assessments(project_id);
CREATE INDEX idx_risk_overall ON risk_assessments(overall_risk);
CREATE INDEX idx_risk_snapshot_id ON risk_assessments(snapshot_id);
-- Latest risk per project
CREATE INDEX idx_risk_project_created ON risk_assessments(project_id, created_at DESC);

-- =============================================================================
-- ALERTS
-- =============================================================================

CREATE TABLE alerts (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id      UUID NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,
    risk_assessment_id UUID REFERENCES risk_assessments(id),
    alert_type      alert_type NOT NULL,
    severity        alert_severity NOT NULL,
    title           TEXT NOT NULL,
    description     TEXT NOT NULL,
    evidence        JSONB,              -- structured evidence (values, thresholds, etc.)
    recommended_action TEXT,
    is_resolved     BOOLEAN DEFAULT FALSE,
    resolved_by     UUID REFERENCES users(id),
    resolved_at     TIMESTAMPTZ,
    resolution_note TEXT,
    report_month    DATE,               -- which period triggered this alert
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_alerts_project_id ON alerts(project_id);
CREATE INDEX idx_alerts_severity ON alerts(severity);
CREATE INDEX idx_alerts_type ON alerts(alert_type);
CREATE INDEX idx_alerts_is_resolved ON alerts(is_resolved);
CREATE INDEX idx_alerts_report_month ON alerts(report_month);

-- =============================================================================
-- ANALYTICS SNAPSHOTS (pre-computed portfolio aggregates)
-- =============================================================================
-- Cached to avoid recomputing expensive aggregates on every dashboard load.
-- Invalidated after each successful import.

CREATE TABLE analytics_snapshots (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_month    DATE,
    scope           TEXT NOT NULL,      -- 'portfolio' | 'sector:Roads' | 'state:Tamil Nadu' | 'ministry:MoRTH'
    metrics         JSONB NOT NULL,     -- arbitrary aggregated metrics
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_analytics_report_month ON analytics_snapshots(report_month);
CREATE INDEX idx_analytics_scope ON analytics_snapshots(scope);

-- =============================================================================
-- ML MODEL VERSIONS
-- =============================================================================

CREATE TABLE model_versions (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name      TEXT NOT NULL,      -- 'cost_overrun_classifier'
    version         TEXT NOT NULL,
    algorithm       TEXT NOT NULL,      -- 'RandomForestClassifier'
    features        JSONB,              -- list of feature names used
    training_period TEXT,               -- 'April 2026 – May 2026'
    metrics         JSONB,              -- precision, recall, F1, AUC
    is_active       BOOLEAN DEFAULT FALSE,
    model_path      TEXT,               -- path to serialized .pkl / .joblib
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (model_name, version)
);

-- =============================================================================
-- ML PREDICTIONS
-- =============================================================================

CREATE TABLE model_predictions (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id          UUID NOT NULL REFERENCES projects(id) ON DELETE RESTRICT,
    snapshot_id         UUID REFERENCES project_snapshots(id),
    model_version_id    UUID REFERENCES model_versions(id),
    prediction_type     TEXT NOT NULL,  -- 'cost_overrun' | 'schedule_delay'
    prediction_value    TEXT,           -- categorical: HIGH / MEDIUM / LOW
    probability         NUMERIC(5, 4),  -- 0.0000–1.0000
    feature_values      JSONB,          -- values of features at prediction time
    explanation         JSONB,          -- feature importances / SHAP values
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_predictions_project_id ON model_predictions(project_id);
CREATE INDEX idx_predictions_model_version ON model_predictions(model_version_id);

-- =============================================================================
-- AUDIT LOGS
-- =============================================================================

CREATE TABLE audit_logs (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id         UUID REFERENCES users(id),
    action          TEXT NOT NULL,      -- 'login', 'upload', 'import', 'resolve_alert', etc.
    entity_type     TEXT,               -- 'project', 'alert', 'import', etc.
    entity_id       TEXT,
    metadata        JSONB,              -- before/after state or additional context
    ip_address      TEXT,
    user_agent      TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_action ON audit_logs(action);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);
CREATE INDEX idx_audit_created_at ON audit_logs(created_at DESC);

-- =============================================================================
-- RISK CONFIGURATION (admin-configurable weights and thresholds)
-- =============================================================================

CREATE TABLE risk_configurations (
    id                          UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name                        TEXT NOT NULL DEFAULT 'default',
    is_active                   BOOLEAN NOT NULL DEFAULT TRUE,

    -- Health dimension weights (must sum to 1.0)
    financial_weight            NUMERIC(4, 3) DEFAULT 0.250,
    schedule_weight             NUMERIC(4, 3) DEFAULT 0.300,
    progress_weight             NUMERIC(4, 3) DEFAULT 0.250,
    milestone_weight            NUMERIC(4, 3) DEFAULT 0.200,

    -- Thresholds for rule-based risk flags
    progress_gap_warning        NUMERIC(5, 2) DEFAULT -10.0,   -- %
    progress_gap_high           NUMERIC(5, 2) DEFAULT -20.0,
    spending_progress_gap_warning NUMERIC(5, 2) DEFAULT 10.0,
    spending_progress_gap_high  NUMERIC(5, 2) DEFAULT 25.0,
    cost_escalation_warning_pct NUMERIC(5, 2) DEFAULT 10.0,
    cost_escalation_high_pct    NUMERIC(5, 2) DEFAULT 25.0,
    schedule_delay_warning_days INTEGER DEFAULT 30,
    schedule_delay_high_days    INTEGER DEFAULT 90,

    -- Health score → risk level thresholds
    health_low_threshold        NUMERIC(5, 2) DEFAULT 75.0,    -- below = medium risk
    health_medium_threshold     NUMERIC(5, 2) DEFAULT 55.0,    -- below = high risk
    health_critical_threshold   NUMERIC(5, 2) DEFAULT 35.0,    -- below = critical

    updated_by                  UUID REFERENCES users(id),
    created_at                  TIMESTAMPTZ DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ DEFAULT NOW()
);

-- Insert default configuration
INSERT INTO risk_configurations (name, is_active) VALUES ('default', TRUE);

-- =============================================================================
-- FOREIGN KEY: documents → project_snapshots (deferred to avoid circular dep)
-- =============================================================================

ALTER TABLE project_snapshots
    ADD CONSTRAINT fk_snapshot_document
    FOREIGN KEY (source_document_id) REFERENCES documents(id);

-- =============================================================================
-- UPDATED_AT TRIGGER
-- =============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_projects_updated_at
    BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_risk_config_updated_at
    BEFORE UPDATE ON risk_configurations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Latest snapshot per project
CREATE OR REPLACE VIEW project_latest_snapshot AS
SELECT DISTINCT ON (ps.project_id)
    ps.*,
    p.project_name,
    p.sector,
    p.state,
    p.ministry,
    p.original_cost,
    p.original_completion_date
FROM project_snapshots ps
JOIN projects p ON ps.project_id = p.id
ORDER BY ps.project_id, ps.report_month DESC;

-- Latest risk assessment per project
CREATE OR REPLACE VIEW project_latest_risk AS
SELECT DISTINCT ON (ra.project_id)
    ra.*,
    p.project_name,
    p.sector,
    p.state,
    p.ministry
FROM risk_assessments ra
JOIN projects p ON ra.project_id = p.id
ORDER BY ra.project_id, ra.created_at DESC;

-- Portfolio summary view
CREATE OR REPLACE VIEW portfolio_summary AS
SELECT
    COUNT(*) FILTER (WHERE lr.overall_risk IS NOT NULL)          AS total_projects,
    COUNT(*) FILTER (WHERE lr.overall_risk = 'low')              AS low_risk_count,
    COUNT(*) FILTER (WHERE lr.overall_risk = 'medium')           AS medium_risk_count,
    COUNT(*) FILTER (WHERE lr.overall_risk = 'high')             AS high_risk_count,
    COUNT(*) FILTER (WHERE lr.overall_risk = 'critical')         AS critical_risk_count,
    AVG(lr.overall_health)                                        AS avg_health_score,
    SUM(p.original_cost)                                          AS total_original_cost,
    SUM(p.revised_cost)                                           AS total_revised_cost,
    SUM(ls.cumulative_expenditure)                                AS total_expenditure
FROM projects p
LEFT JOIN project_latest_risk lr ON lr.project_id = p.id
LEFT JOIN project_latest_snapshot ls ON ls.project_id = p.id;

-- =============================================================================
-- END OF SCHEMA
-- =============================================================================
