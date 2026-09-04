# PAIMANA Project Intelligence & Early Warning System

> A web-based infrastructure project monitoring platform that transforms PAIMANA project data into project-health insights, risk indicators, forecasts, and early-warning notifications for infrastructure monitoring teams.

---

## Table of Contents

1. [Project Overview & Problem Statement](#1-project-overview--problem-statement)
2. [Our Solution](#2-our-solution)
3. [Tech Stack & Framework](#3-tech-stack--framework)
4. [System Architecture](#4-system-architecture)
5. [Database Schema & Data Integrity](#5-database-schema--data-integrity)
6. [Key Features](#6-key-features)
7. [Application Route Map](#7-application-route-map)
8. [Folder Structure](#8-folder-structure)
9. [Setup & Installation](#9-setup--installation)
10. [Environment Variables](#10-environment-variables)
11. [Running Locally](#11-running-locally)
12. [Build & Deployment](#12-build--deployment)
13. [Testing](#13-testing)
14. [Data Ingestion Workflow](#14-data-ingestion-workflow)
15. [Analytics, Risk & Prediction](#15-analytics-risk--prediction)
16. [Security](#16-security)
17. [Performance, Scalability & Reliability](#17-performance-scalability--reliability)
18. [Contributing](#18-contributing)
19. [License](#19-license)
20. [Project Status](#20-project-status)

---

# 1. Project Overview & Problem Statement

## 1.1 Problem Statement

### SIH Problem Statement ID

**26103**

### Title

**Use case on web-based integrated project-monitoring platform**

### Organization

**Ministry of Statistics and Programme Implementation (MoSPI)**

### Department

**Data Informatics & Innovation Division (DIID)**

### Category

**Software**

### Theme

**Smart Automation**

---

## 1.2 Problem Context

The Infrastructure & Project Monitoring Division (IPMD), Ministry of Statistics and Programme Implementation (MoSPI), monitors major Central Sector infrastructure projects.

The existing project-monitoring ecosystem, including the historical OCMS system and the modern PAIMANA platform, contains project information such as:

* Project cost
* Revised cost
* Expenditure
* Project timelines
* Physical progress
* Milestones
* Implementing agencies
* Project status
* Sector
* Ministry / Department
* Geographic information

The problem is that infrastructure projects can gradually develop:

* Cost overruns
* Time overruns
* Delayed milestones
* Progress deviations
* Financial inefficiencies
* Implementation bottlenecks
* Resource constraints
* Execution risks

Traditional monitoring is primarily useful for answering:

> **"What is the current status of the project?"**

The desired system should move toward answering:

> **"Which projects are showing warning signs, why are they at risk, and which projects require attention?"**

The SIH problem statement therefore proposes moving from descriptive monitoring toward predictive and prescriptive decision support.

---

## 1.3 Target Users

The primary users of the platform are expected to include:

| User                            | Primary Needs                                    |
| ------------------------------- | ------------------------------------------------ |
| Ministry / Department Officials | Portfolio-level monitoring and decision support  |
| Project Monitoring Officers     | Project-level health, progress and warnings      |
| Senior Administrators           | High-level dashboards and priority interventions |
| Implementing Agencies           | Project updates and milestone tracking           |
| Data Administrators             | Data ingestion, validation and management        |
| Analysts                        | Historical analysis, benchmarking and reporting  |

---

## 1.4 User Pain Points

The platform addresses several operational challenges:

### Fragmented project information

Project data contains many dimensions such as financial information, timelines, progress and milestones. Without an integrated interface, identifying important relationships across these fields is difficult.

### Reactive monitoring

Problems may only become visible after delays or cost escalation are already significant.

### Difficulty prioritizing projects

When hundreds or thousands of projects are being monitored, officials need a mechanism for identifying which projects deserve immediate attention.

### Limited visibility into trends

A single snapshot does not provide enough information to understand whether a project is improving, deteriorating or remaining stable.

### Manual interpretation

Raw project data still needs to be interpreted by monitoring teams before an intervention decision can be made.

---

# 2. Our Solution

## 2.1 Solution Overview

We propose a **web-based infrastructure project monitoring and early-warning platform** that converts project monitoring data into structured, actionable information.

The system will:

1. Accept project data from supported sources such as PDF, Excel and CSV files.
2. Extract and normalize project information.
3. Store project data and historical snapshots in a structured database.
4. Calculate project-performance indicators.
5. Identify deviations and potential risk conditions.
6. Generate project-health scores.
7. Provide early-warning alerts.
8. Provide trend and comparative analytics.
9. Support statistical forecasting.
10. Provide an optional predictive ML layer when sufficient historical data is available.
11. Present all outputs through a centralized web dashboard.

---

## 2.2 Core Value Proposition

The platform transforms:

```text
Raw Project Data
       ↓
Structured Project Records
       ↓
Performance Metrics
       ↓
Risk Indicators
       ↓
Forecasts / Predictions
       ↓
Early Warnings
       ↓
Actionable Dashboard
```

Instead of requiring an officer to manually inspect thousands of project records, the system highlights projects that require attention.

---

## 2.3 Key Differentiators

### 1. Data-source independent ingestion

The architecture separates data ingestion from analytics.

The initial system can process:

* PDF reports
* Excel files
* CSV files

and can later be extended to consume APIs.

### 2. Historical project tracking

Projects are stored as time-based snapshots rather than only as current records.

Example:

```text
Project 705728

April 2026
    ↓
May 2026
    ↓
June 2026
    ↓
July 2026
    ↓
...
```

This enables trend analysis.

### 3. Explainable risk analysis

Instead of showing only:

```text
Risk = HIGH
```

the platform should explain:

```text
Why?

• Progress is significantly below planned progress.
• Expenditure is ahead of physical progress.
• Multiple milestones are delayed.
• Completion date has shifted.
```

### 4. Layered intelligence

The system is intentionally designed in multiple levels:

```text
Monitoring
   ↓
Analytics
   ↓
Rule-based Risk Detection
   ↓
Statistical Forecasting
   ↓
Optional ML Prediction
```

This allows the platform to remain useful even when historical data is insufficient for advanced ML.

### 5. Decision-oriented design

The platform is designed around the question:

> **Which projects require attention and why?**

rather than simply displaying raw data.

---

# 3. Tech Stack & Framework

> **Note:** Final versions should be pinned in the repository's lockfiles once implementation begins. The table below describes the intended stack; values marked `TBD` must be updated to the actual versions used.

## 3.1 Frontend

| Technology   | Purpose                   | Version |
| ------------ | ------------------------- | ------- |
| Next.js      | Web application framework | TBD     |
| React        | UI framework              | TBD     |
| TypeScript   | Type-safe development     | TBD     |
| Tailwind CSS | Styling                   | TBD     |
| shadcn/ui    | UI components             | TBD     |
| Recharts     | Data visualization        | TBD     |

---

## 3.2 Backend

| Technology | Purpose                         | Version |
| ---------- | ------------------------------- | ------- |
| Python     | Data/analytics backend          | TBD     |
| FastAPI    | REST API and processing service | TBD     |
| Pydantic   | Request/response validation     | TBD     |
| Uvicorn    | ASGI server                     | TBD     |

---

## 3.3 Data Processing

| Technology                   | Purpose              | Version |
| ---------------------------- | -------------------- | ------- |
| Pandas                       | Data manipulation    | TBD     |
| NumPy                        | Numerical operations | TBD     |
| OpenPyXL                     | Excel ingestion      | TBD     |
| PDF/table extraction library | PDF data extraction  | TBD     |

The final PDF extraction library will depend on the exact structure of the supplied PAIMANA reports.

---

## 3.4 Analytics / Prediction

| Technology   | Purpose              | Version |
| ------------ | -------------------- | ------- |
| Pandas       | Feature preparation  | TBD     |
| NumPy        | Numerical processing | TBD     |
| SciPy        | Statistical analysis | TBD     |
| scikit-learn | Optional ML models   | TBD     |

The predictive layer will initially prioritize simple, interpretable models instead of unnecessarily complex deep-learning architectures.

---

## 3.5 Database

### PostgreSQL

PostgreSQL is the primary relational database.

**Reason for selection:**

* Strong relational modeling
* Transactions
* Constraints
* Indexes
* Aggregation
* Structured historical data
* Excellent support for analytical queries
* Suitable for project, milestone and monthly-snapshot relationships

### Supabase

Supabase can be used as the managed PostgreSQL platform and can additionally provide:

* Authentication
* Database hosting
* Storage
* Row-level security
* APIs

---

## 3.6 Development Tools

Expected tooling:

```text
Git
GitHub
VS Code
Node.js
npm / pnpm
Python
pip / uv
Docker (optional)
Postman / Insomnia
```

Final choices should be documented in the repository once development begins.

---

## 3.7 Third-Party Services

Potential integrations:

| Service                 | Purpose                   |
| ----------------------- | ------------------------- |
| Supabase                | PostgreSQL, Auth, Storage |
| Vercel                  | Frontend deployment       |
| Python hosting provider | Analytics/API service     |
| PAIMANA                 | Source/reference data     |
| Email provider          | Notifications, optional   |

No external AI API is required for the core monitoring system.

---

# 4. System Architecture

## 4.1 Architectural Pattern

The recommended architecture is a:

> **Layered, service-oriented web architecture**

with separate responsibilities for:

* Frontend
* API/backend
* Data ingestion
* Database
* Analytics
* Risk engine
* Prediction service

It does not need to begin as a complex microservices system.

The initial implementation should remain a modular architecture that can later be separated into services if scale requires it.

---

## 4.2 High-Level Architecture

```text
                         ┌──────────────────────┐
                         │      DATA SOURCES    │
                         ├──────────────────────┤
                         │ PDF                  │
                         │ Excel                │
                         │ CSV                  │
                         │ API (future)         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   INGESTION SERVICE  │
                         │                      │
                         │ PDF Parser            │
                         │ Excel Parser          │
                         │ CSV Parser            │
                         │ Validation             │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   RAW FILE STORAGE   │
                         │                      │
                         │ Original reports     │
                         │ Metadata              │
                         │ Import status         │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ NORMALIZATION LAYER  │
                         │                      │
                         │ Cleaning              │
                         │ Date normalization    │
                         │ Numeric normalization │
                         │ Validation             │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────────┐
                    │           POSTGRESQL             │
                    │                                  │
                    │ Projects                         │
                    │ Project Snapshots                │
                    │ Milestones                       │
                    │ Organizations                    │
                    │ Alerts                           │
                    │ Documents                        │
                    └───────────────┬──────────────────┘
                                    │
                ┌───────────────────┼────────────────────┐
                │                   │                    │
                ▼                   ▼                    ▼
       ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐
       │ Analytics      │  │ Risk Engine    │  │ Prediction      │
       │ Engine         │  │                │  │ Engine          │
       └───────┬────────┘  └───────┬────────┘  └────────┬────────┘
               │                   │                    │
               └───────────────────┼────────────────────┘
                                   ▼
                         ┌─────────────────────┐
                         │ DECISION ENGINE     │
                         │                     │
                         │ Health Score        │
                         │ Risk Level          │
                         │ Warnings            │
                         │ Forecasts           │
                         │ Explanations        │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FASTAPI API     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │      NEXT.JS        │
                         │    WEB PLATFORM     │
                         └─────────────────────┘
```

---

## 4.3 Request Flow

### Example: project details request

```text
Browser
   ↓
Next.js page
   ↓
API request
   ↓
FastAPI
   ↓
Authorization
   ↓
Project service
   ↓
PostgreSQL
   ↓
Project + snapshots + milestones
   ↓
Analytics calculation
   ↓
Risk/health calculation
   ↓
API response
   ↓
Next.js
   ↓
Dashboard
```

---

## 4.4 Data Ingestion Flow

```text
User Uploads Report
        ↓
File Type Detection
        ↓
PDF / Excel / CSV Parser
        ↓
Raw Extracted Rows
        ↓
Column Mapping
        ↓
Data Validation
        ↓
Normalization
        ↓
Project ID Matching
        ↓
Historical Snapshot Creation
        ↓
Database
        ↓
Analytics / Risk Processing
```

---

## 4.5 External Communication

### Browser → Backend

```text
HTTPS
REST API
JSON
```

### Backend → Database

```text
PostgreSQL protocol
TLS in production
```

### Backend → File Storage

```text
HTTPS
```

### Future PAIMANA API Integration

```text
HTTPS
REST / JSON
```

---

# 5. Database Schema & Data Integrity

## 5.1 Database Choice

**PostgreSQL**

The data naturally represents relational entities and time-based project observations.

A relational database is preferable to a NoSQL database because:

* Projects have structured relationships.
* Project snapshots belong to specific projects.
* Milestones belong to projects.
* Organizations are shared across projects.
* Queries require joins and aggregations.
* Financial and timeline calculations benefit from strong typing and constraints.

---

# 5.2 Entity Relationship Overview

```text
organizations
      │
      │ 1:N
      ▼
   projects
      │
      ├──────────────┐
      │              │
      │ 1:N          │ 1:N
      ▼              ▼
project_snapshots  milestones
      │
      │ 1:N
      ▼
risk_assessments
      │
      │ 1:N
      ▼
alerts

projects
   │
   │ 1:N
   ▼
documents
```

---

# 5.3 `organizations`

Stores ministries, departments, agencies and other organizational entities.

```sql
CREATE TABLE organizations (
    id UUID PRIMARY KEY,
    name TEXT NOT NULL,
    organization_type TEXT NOT NULL,
    code TEXT UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

# 5.4 `projects`

Stores the stable identity and master information of a project.

```sql
CREATE TABLE projects (
    id UUID PRIMARY KEY,

    project_id TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL,

    organization_id UUID
        REFERENCES organizations(id)
        ON DELETE SET NULL,

    ministry TEXT,
    department TEXT,
    agency TEXT,

    sector TEXT,
    state TEXT,

    original_cost NUMERIC(20,2),
    revised_cost NUMERIC(20,2),

    original_start_date DATE,
    original_completion_date DATE,
    revised_completion_date DATE,

    status TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

# 5.5 `project_snapshots`

Stores the state of a project for a particular reporting period.

This is one of the most important tables in the system.

```sql
CREATE TABLE project_snapshots (
    id UUID PRIMARY KEY,

    project_id UUID NOT NULL
        REFERENCES projects(id)
        ON DELETE CASCADE,

    report_month DATE NOT NULL,

    physical_progress NUMERIC(7,3),
    planned_progress NUMERIC(7,3),

    cumulative_expenditure NUMERIC(20,2),

    current_cost NUMERIC(20,2),

    current_completion_date DATE,

    current_status TEXT,

    source_document_id UUID,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE(project_id, report_month)
);
```

---

# 5.6 `milestones`

```sql
CREATE TABLE milestones (
    id UUID PRIMARY KEY,

    project_id UUID NOT NULL
        REFERENCES projects(id)
        ON DELETE CASCADE,

    milestone_name TEXT NOT NULL,

    planned_date DATE,
    actual_date DATE,

    status TEXT,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

# 5.7 `documents`

Stores original uploaded files.

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,

    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,

    storage_path TEXT NOT NULL,

    report_month DATE,

    file_hash TEXT UNIQUE,

    processing_status TEXT NOT NULL,

    uploaded_by UUID,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

# 5.8 `risk_assessments`

```sql
CREATE TABLE risk_assessments (
    id UUID PRIMARY KEY,

    project_id UUID NOT NULL
        REFERENCES projects(id)
        ON DELETE CASCADE,

    snapshot_id UUID
        REFERENCES project_snapshots(id)
        ON DELETE CASCADE,

    health_score NUMERIC(6,2),

    financial_risk NUMERIC(6,2),
    schedule_risk NUMERIC(6,2),
    progress_risk NUMERIC(6,2),

    overall_risk TEXT,

    prediction_probability NUMERIC(6,5),

    explanation JSONB,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

# 5.9 `alerts`

```sql
CREATE TABLE alerts (
    id UUID PRIMARY KEY,

    project_id UUID NOT NULL
        REFERENCES projects(id)
        ON DELETE CASCADE,

    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,

    title TEXT NOT NULL,
    description TEXT,

    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);
```

---

# 5.10 Relationships

| Relationship               | Cardinality                    |
| -------------------------- | ------------------------------ |
| Organization → Projects    | 1:N                            |
| Project → Snapshots        | 1:N                            |
| Project → Milestones       | 1:N                            |
| Project → Documents        | 1:N                            |
| Project → Risk Assessments | 1:N                            |
| Project → Alerts           | 1:N                            |
| Snapshot → Risk Assessment | 1:N / implementation-dependent |

---

# 5.11 Indexing Strategy

Recommended indexes:

```sql
CREATE INDEX idx_projects_sector
ON projects(sector);

CREATE INDEX idx_projects_state
ON projects(state);

CREATE INDEX idx_projects_status
ON projects(status);

CREATE INDEX idx_snapshots_project_month
ON project_snapshots(project_id, report_month);

CREATE INDEX idx_alerts_project
ON alerts(project_id);

CREATE INDEX idx_alerts_severity
ON alerts(severity);
```

Additional indexes should be introduced based on actual query performance.

---

# 5.12 Data Integrity

The system should use:

* Primary keys
* Foreign keys
* Unique constraints
* NOT NULL constraints where appropriate
* Numeric type validation
* Date validation
* Enum/check constraints where appropriate
* Transactional imports
* Duplicate detection
* File hashing

### Example

A project/month combination must not be imported twice:

```sql
UNIQUE(project_id, report_month)
```

---

# 5.13 Import Transactions

A complete import should behave atomically.

```text
Start transaction
      ↓
Import file metadata
      ↓
Validate rows
      ↓
Insert/update projects
      ↓
Insert snapshots
      ↓
Create analytics
      ↓
Commit

OR

Any critical error
      ↓
Rollback
```

This avoids partially imported reports.

---

# 5.14 Migration Strategy

Database migrations should be version-controlled.

Recommended approach:

```text
database/
└── migrations/
    ├── 001_initial_schema.sql
    ├── 002_add_risk_assessments.sql
    ├── 003_add_alerts.sql
    └── ...
```

---

# 6. Key Features

## 6.1 Executive Dashboard

Displays:

* Total projects
* Projects on track
* Projects requiring attention
* High-risk projects
* Financial statistics
* Progress statistics
* Sector distribution
* State distribution
* Ministry distribution

---

## 6.2 Project Explorer

Search and filter by:

* Project ID
* Project name
* Ministry
* Department
* Agency
* Sector
* State
* Status
* Risk level

---

## 6.3 Project Details

Each project should provide:

```text
Project Information
        ↓
Financial Overview
        ↓
Physical Progress
        ↓
Timeline
        ↓
Milestones
        ↓
Historical Trend
        ↓
Risk Analysis
        ↓
Early Warnings
```

---

## 6.4 Project Health Score

Each project receives an interpretable health score derived from multiple indicators.

Example:

```text
Overall Health: 68 / 100

Financial Health: 74
Schedule Health:  54
Progress Health:  72
Milestone Health: 61
```

---

## 6.5 Risk Classification

Example categories:

```text
LOW
MEDIUM
HIGH
CRITICAL
```

Thresholds will be configurable and should be validated during implementation.

---

## 6.6 Early Warning System

The system identifies conditions such as:

* Progress significantly below plan
* Spending ahead of physical progress
* Delayed milestones
* Completion date revisions
* Cost escalation
* Deteriorating progress trend

---

## 6.7 Analytics

Supported analysis should include:

* Cost variance
* Schedule variance
* Progress variance
* Expenditure-to-progress comparison
* Sector comparison
* Ministry comparison
* State comparison
* Project ranking
* Historical trends

---

## 6.8 Forecasting

Potential forecast outputs:

* Expected completion timeline
* Expected expenditure
* Progress trajectory
* Potential cost escalation
* Potential delay

---

## 6.9 Optional Predictive ML

When sufficient historical data exists, a predictive model may estimate:

```text
Cost-overrun probability
Schedule-risk probability
Project risk category
```

ML remains an enhancement over the core monitoring system.

---

## 6.10 Report Generation

Potential exports:

```text
PDF
CSV
Excel
```

Reports can contain:

* Project summary
* Health score
* Risk factors
* Trend charts
* Alerts
* Forecasts

---

## 6.11 Authentication

Expected authentication capabilities:

* Email/password or SSO-compatible authentication
* Session management
* Protected routes
* Role-based access
* Secure password handling through the selected identity provider

---

## 6.12 Authorization

Possible roles:

```text
ADMIN
ANALYST
OFFICER
VIEWER
```

Permissions should be enforced server-side.

---

# 7. Application Route Map

The following is the **proposed route map**. Final paths must be synchronized with the implementation.

---

## 7.1 Frontend Routes

| Method | Route                    | Description             | Auth     |
| ------ | ------------------------ | ----------------------- | -------- |
| GET    | `/`                      | Landing/login page      | Public   |
| GET    | `/dashboard`             | Executive dashboard     | Required |
| GET    | `/projects`              | Project explorer        | Required |
| GET    | `/projects/[id]`         | Project details         | Required |
| GET    | `/projects/[id]/history` | Historical project data | Required |
| GET    | `/projects/[id]/risk`    | Risk analysis           | Required |
| GET    | `/alerts`                | Early-warning center    | Required |
| GET    | `/analytics`             | Portfolio analytics     | Required |
| GET    | `/reports`               | Generated reports       | Required |
| GET    | `/admin`                 | Administration          | Admin    |
| GET    | `/admin/data-import`     | Data ingestion          | Admin    |
| GET    | `/settings`              | User settings           | Required |

---

# 7.2 API Routes

## Authentication

### `POST /api/auth/login`

Authenticate a user.

Example request:

```json
{
  "email": "officer@example.gov",
  "password": "********"
}
```

Example response:

```json
{
  "user": {
    "id": "user-id",
    "role": "OFFICER"
  },
  "session": {
    "expires_at": "2026-09-04T12:00:00Z"
  }
}
```

---

## Projects

### `GET /api/projects`

Retrieve projects.

Query parameters:

```text
?page=1
&limit=20
&sector=Transport
&state=Tamil Nadu
&risk=HIGH
```

Example:

```json
{
  "data": [
    {
      "project_id": "705728",
      "project_name": "Example Project",
      "sector": "Transport",
      "state": "Example State",
      "risk": "HIGH"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1981
  }
}
```

Authentication: Required.

---

### `GET /api/projects/{projectId}`

Returns complete project information.

Authentication: Required.

---

### `GET /api/projects/{projectId}/history`

Returns chronological project snapshots.

Example response:

```json
{
  "project_id": "705728",
  "snapshots": [
    {
      "month": "2026-04",
      "progress": 59.86,
      "expenditure": 90502
    },
    {
      "month": "2026-06",
      "progress": 60.87,
      "expenditure": 90967
    }
  ]
}
```

---

## Risk

### `GET /api/projects/{projectId}/risk`

Returns the latest risk assessment.

Example:

```json
{
  "health_score": 64,
  "overall_risk": "HIGH",
  "financial_risk": 72,
  "schedule_risk": 81,
  "progress_risk": 63,
  "warnings": [
    {
      "type": "SCHEDULE",
      "severity": "HIGH",
      "message": "Progress is below the expected trajectory."
    }
  ]
}
```

---

## Alerts

### `GET /api/alerts`

Retrieve alerts.

Parameters:

```text
severity
status
sector
state
page
limit
```

Authentication: Required.

---

### `PATCH /api/alerts/{alertId}`

Resolve or update an alert.

Example:

```json
{
  "is_resolved": true
}
```

Authentication: Officer/Admin.

---

# 7.3 Data Import

### `POST /api/import`

Upload a supported source file.

Supported formats:

```text
.pdf
.xlsx
.csv
```

Multipart request:

```text
file=<uploaded file>
report_month=2026-06-01
```

Example response:

```json
{
  "import_id": "import-123",
  "status": "PROCESSING"
}
```

Authentication: Admin / authorized data operator.

---

### `GET /api/import/{importId}`

Check import status.

Example:

```json
{
  "import_id": "import-123",
  "status": "COMPLETED",
  "rows_processed": 1847,
  "rows_rejected": 0
}
```

---

# 7.4 Analytics

### `GET /api/analytics/overview`

Returns aggregated portfolio metrics.

Example:

```json
{
  "total_projects": 1981,
  "low_risk": 1284,
  "medium_risk": 421,
  "high_risk": 276
}
```

---

### `GET /api/analytics/sectors`

Returns sector-level statistics.

---

### `GET /api/analytics/states`

Returns state-level statistics.

---

### `GET /api/analytics/ministries`

Returns ministry-level statistics.

---

# 7.5 Reports

### `POST /api/reports/project/{projectId}`

Generate a project report.

---

### `GET /api/reports/{reportId}`

Retrieve generated report metadata/download link.

---

# 7.6 Middleware

Expected middleware layers:

```text
Request
  ↓
CORS
  ↓
Authentication
  ↓
Authorization
  ↓
Rate limiting
  ↓
Validation
  ↓
Controller
  ↓
Service
  ↓
Database
```

---

# 7.7 Validation

Use schema validation for:

* Uploaded file type
* File size
* Dates
* Numeric fields
* Project IDs
* Percentages
* Pagination
* Filter parameters

---

# 7.8 Rate Limiting

Public endpoints should be rate-limited.

High-cost operations such as:

```text
Data import
Report generation
Heavy analytics
```

should receive stricter rate limits.

Exact values should be configured after deployment requirements are known.

---

# 8. Folder Structure

The following represents the recommended repository structure.

```text
paimana-monitor/
│
├── README.md
├── LICENSE
├── .gitignore
├── .env.example
├── docker-compose.yml
│
├── frontend/
│   ├── app/
│   │   ├── dashboard/
│   │   ├── projects/
│   │   ├── alerts/
│   │   ├── analytics/
│   │   ├── reports/
│   │   ├── admin/
│   │   ├── settings/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   │
│   ├── components/
│   │   ├── dashboard/
│   │   ├── projects/
│   │   ├── alerts/
│   │   ├── analytics/
│   │   ├── charts/
│   │   └── ui/
│   │
│   ├── lib/
│   │   ├── api/
│   │   ├── auth/
│   │   ├── validation/
│   │   └── utils/
│   │
│   ├── hooks/
│   ├── types/
│   ├── public/
│   ├── tests/
│   ├── package.json
│   └── tsconfig.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── projects.py
│   │   │   │   ├── alerts.py
│   │   │   │   ├── analytics.py
│   │   │   │   ├── imports.py
│   │   │   │   └── reports.py
│   │   │   └── dependencies.py
│   │   │
│   │   ├── services/
│   │   │   ├── project_service.py
│   │   │   ├── import_service.py
│   │   │   ├── analytics_service.py
│   │   │   ├── risk_service.py
│   │   │   └── report_service.py
│   │   │
│   │   ├── ingestion/
│   │   │   ├── pdf_parser.py
│   │   │   ├── excel_parser.py
│   │   │   ├── csv_parser.py
│   │   │   ├── normalizer.py
│   │   │   └── validator.py
│   │   │
│   │   ├── analytics/
│   │   │   ├── metrics.py
│   │   │   ├── trends.py
│   │   │   └── forecasts.py
│   │   │
│   │   ├── risk/
│   │   │   ├── rules.py
│   │   │   ├── scoring.py
│   │   │   └── explanations.py
│   │   │
│   │   ├── ml/
│   │   │   ├── features.py
│   │   │   ├── train.py
│   │   │   ├── predict.py
│   │   │   └── evaluation.py
│   │   │
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── database/
│   │   └── config/
│   │
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   │
│   ├── requirements.txt
│   └── pyproject.toml
│
├── database/
│   ├── migrations/
│   ├── seeds/
│   └── schema/
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── samples/
│   └── README.md
│
├── notebooks/
│   ├── data_exploration/
│   ├── analytics/
│   └── experiments/
│
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── database/
│   └── decisions/
│
└── scripts/
    ├── import_data.py
    ├── validate_data.py
    ├── seed_database.py
    └── generate_report.py
```

---

## 8.1 Directory Responsibilities

### `frontend/`

Contains the Next.js application.

### `backend/`

Contains API, data ingestion, analytics and prediction services.

### `database/`

Contains database migrations, schema definitions and seed data.

### `data/`

Local development data only.

Production uploads should use managed storage.

### `notebooks/`

Used for:

* data exploration
* analysis
* experimentation
* model evaluation

Notebooks should not contain production application logic.

### `docs/`

Project architecture, API and technical documentation.

### `scripts/`

Reusable CLI scripts for development and data operations.

---

## 8.2 Naming Conventions

### TypeScript

```text
PascalCase.tsx
camelCase.ts
```

### Python

```text
snake_case.py
```

### Database

```text
snake_case
```

### React Components

```text
ProjectCard.tsx
RiskBadge.tsx
HealthScore.tsx
```

### Services

```text
project_service.py
risk_service.py
analytics_service.py
```

---

# 9. Setup & Installation

## 9.1 Prerequisites

Install:

```text
Node.js
npm or pnpm
Python
pip
PostgreSQL / Supabase account
Git
```

Optional:

```text
Docker
Postman
```

Recommended versions will be pinned once implementation begins.

---

# 9.2 Clone Repository

```bash
git clone <REPOSITORY_URL>
cd paimana-monitor
```

---

# 9.3 Frontend Installation

```bash
cd frontend
npm install
```

---

# 9.4 Backend Installation

```bash
cd backend

python -m venv .venv
```

Activate:

### Linux/macOS

```bash
source .venv/bin/activate
```

### Windows

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 9.5 Database Setup

Create a PostgreSQL database through Supabase or another PostgreSQL provider.

Run migrations:

```bash
# Example migration command
<database-migration-command>
```

The actual migration tooling will be finalized during implementation.

---

# 10. Environment Variables

Create:

```text
.env.local
```

for the frontend and:

```text
.env
```

for the backend.

---

## 10.1 Frontend

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
```

---

## 10.2 Backend

```env
DATABASE_URL=
SUPABASE_URL=
SUPABASE_SERVICE_ROLE_KEY=

JWT_SECRET=
ENVIRONMENT=development

CORS_ORIGINS=http://localhost:3000

STORAGE_BUCKET=
```

---

## 10.3 Optional ML Configuration

```env
MODEL_PATH=
MODEL_VERSION=
```

---

## 10.4 Security Rules

Never commit:

```text
.env
.env.local
.env.production
```

to Git.

Only commit:

```text
.env.example
```

with empty or placeholder values.

---

# 11. Running Locally

## 11.1 Start Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Backend:

```text
http://localhost:8000
```

API documentation:

```text
http://localhost:8000/docs
```

---

## 11.2 Start Frontend

```bash
cd frontend
npm run dev
```

Frontend:

```text
http://localhost:3000
```

---

# 12. Build & Deployment

## 12.1 Frontend

Build:

```bash
npm run build
```

Run production build:

```bash
npm run start
```

Recommended deployment platform:

```text
Vercel
```

---

## 12.2 Backend

Production server:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Containerized deployment may be used when required.

---

## 12.3 Database

Production PostgreSQL should use:

* TLS
* automated backups
* restricted credentials
* connection pooling
* monitoring

---

# 13. Testing

## 13.1 Testing Strategy

The project should use multiple layers of testing.

```text
Unit Tests
    ↓
Integration Tests
    ↓
API Tests
    ↓
Database Tests
    ↓
Frontend Tests
    ↓
End-to-End Tests
```

---

## 13.2 Backend Tests

Recommended tools:

```text
pytest
httpx
```

Run:

```bash
pytest
```

---

## 13.3 Frontend Tests

Recommended stack:

```text
Vitest
Testing Library
Playwright
```

Example:

```bash
npm run test
```

---

## 13.4 Data Pipeline Tests

Every parser should be tested against sample reports.

Example:

```text
Input:
April 2026 report

Expected:
- Project rows extracted
- Project IDs present
- Numeric fields normalized
- Dates valid
- Duplicate detection works
```

---

## 13.5 Model Evaluation

If ML is enabled, models should be evaluated using an appropriate time-aware validation methodology rather than relying only on random splits.

Possible metrics:

### Classification

```text
Accuracy
Precision
Recall
F1
ROC-AUC
Confusion Matrix
```

### Regression

```text
MAE
RMSE
R²
```

The chosen metric should match the business objective.

---

# 14. Data Ingestion Workflow

## 14.1 Supported Inputs

Initial system:

```text
PDF
Excel
CSV
```

Future:

```text
PAIMANA API
```

---

## 14.2 File Upload

Admin uploads:

```text
FlashReport_June_2026.pdf
```

System detects:

```text
Report Month = June 2026
```

---

## 14.3 Extraction

The parser locates relevant project tables.

Example:

```text
Project ID
Project Name
Agency
Cost
Expenditure
Progress
Dates
...
```

---

## 14.4 Normalization

Examples:

```text
"60.87%" → 60.87

"31/12/2026" → 2026-12-31

"₹90,967 Cr" → 90967
```

---

## 14.5 Project Matching

Project ID is the primary matching key whenever available.

Example:

```text
April
Project ID = 705728

May
Project ID = 705728

June
Project ID = 705728
```

These records become historical observations for the same project.

---

## 14.6 Validation

Examples:

```text
Progress must be 0–100
Cost must be >= 0
Dates must be valid
Project ID must not be blank
Report month must be valid
```

---

# 15. Analytics, Risk & Prediction

## 15.1 Basic Project Metrics

### Time Consumed

```text
elapsed_time / planned_duration × 100
```

### Progress Gap

```text
actual_progress - planned_progress
```

### Cost Variance

```text
(revised_cost - original_cost)
/
original_cost × 100
```

### Spending vs Progress

```text
expenditure_percentage
-
physical_progress_percentage
```

These calculations provide the foundation for project monitoring.

---

# 15.2 Example

Suppose:

```text
Road Project
-------------------------
Contract value     ₹1,00,000
Duration           20 days
Current day        17
Progress           68%
Expenditure        ₹80,000
```

Time consumed:

```text
17 / 20 × 100
= 85%
```

Money consumed:

```text
80%
```

Progress:

```text
68%
```

Progress gap:

```text
68 - 85
= -17%
```

Spending vs progress:

```text
80 - 68
= +12%
```

The system can therefore generate warnings such as:

```text
Schedule Warning
Financial Efficiency Warning
```

---

# 15.3 Rule-Based Risk Engine

Example rules:

```text
IF progress_gap <= -10
THEN schedule_risk = HIGH
```

```text
IF spending_progress_gap >= 10
THEN financial_risk = HIGH
```

```text
IF revised_cost > original_cost
THEN cost_escalation = TRUE
```

```text
IF revised_completion_date > original_completion_date
THEN schedule_escalation = TRUE
```

Actual thresholds should be configurable rather than hard-coded.

---

# 15.4 Health Score

A project-health score may combine:

```text
Financial Health
Schedule Health
Physical Progress Health
Milestone Health
```

Example:

```text
Health Score = 68 / 100
Risk Level   = HIGH
```

The weighting methodology should be documented and validated during development.

---

# 15.5 Statistical Forecasting

Forecasting can estimate values such as:

```text
Expected completion date
Expected expenditure
Progress trajectory
```

Example:

```text
Current progress     = 68%
Remaining progress   = 32%
Remaining duration   = 3 days
```

The system analyzes historical progress velocity to determine whether completing the remaining work inside the original schedule is plausible.

---

# 15.6 Machine Learning Layer

ML should be introduced only after the historical dataset is validated.

Example:

```text
Input Features
-------------------------
Original Cost
Expenditure
Physical Progress
Progress Gap
Time Used
Spending Gap
Sector
State
Agency
Delayed Milestones
...
```

Model output:

```text
Cost Overrun Probability = 0.78
Risk = HIGH
```

The UI should transform that into an understandable explanation rather than exposing raw model output alone.

---

# 15.7 Avoiding Data Leakage

The model must not receive information that directly reveals the target outcome.

For example, when predicting future cost overrun:

```text
Current revised final cost
```

should not be used as an input if the target is:

```text
Whether the project will eventually exceed its original cost
```

Instead, the model should use only information available at prediction time.

---

# 16. Security

## 16.1 Authentication

Authentication should be handled by a trusted identity system.

All protected API routes must verify the authenticated user.

---

## 16.2 Authorization

Access should be role-based.

Example:

```text
VIEWER
  ↓
Read-only

OFFICER
  ↓
Read + manage assigned workflows

ANALYST
  ↓
Read + analytics

ADMIN
  ↓
Full management
```

---

## 16.3 Data Security

Production deployment should use:

* HTTPS
* Secure HTTP-only cookies where applicable
* Environment secrets
* Database TLS
* Restricted service credentials
* Server-side authorization
* Input validation
* File type validation
* File size limits
* Audit logs

---

## 16.4 Uploaded Files

Uploaded files must be treated as untrusted input.

The system should:

1. Validate extension.
2. Validate MIME/content type.
3. Enforce size limits.
4. Generate unique storage names.
5. Store outside the executable application directory.
6. Scan where appropriate.
7. Never execute uploaded content.

---

# 17. Performance, Scalability & Reliability

## 17.1 Performance

Optimize through:

* Database indexing
* Pagination
* Server-side filtering
* Aggregated queries
* Query caching
* Lazy loading
* Chart data aggregation
* Background imports

---

## 17.2 Caching

Potential cache targets:

```text
Dashboard summary
Sector statistics
State statistics
Ministry statistics
Frequently accessed project information
```

The cache must be invalidated after significant data imports.

---

## 17.3 Background Jobs

Heavy tasks should not block HTTP requests.

Examples:

```text
PDF extraction
Large Excel import
Risk calculation
Report generation
Model inference
```

Recommended architecture:

```text
HTTP Request
     ↓
Create Job
     ↓
Background Worker
     ↓
Process
     ↓
Update Job Status
     ↓
Frontend Polls / Receives Status
```

---

## 17.4 Scalability

The system should be able to scale horizontally.

```text
                Load Balancer
                      │
         ┌────────────┼────────────┐
         ↓            ↓            ↓
      API-1         API-2        API-3
         └────────────┼────────────┘
                      ↓
                PostgreSQL
```

Analytics workloads can later be separated from transactional workloads if required.

---

## 17.5 Reliability

Production deployment should include:

* Database backups
* Health checks
* Error logging
* Structured logging
* Monitoring
* Import retry mechanisms
* Idempotent processing
* Transaction rollback
* Graceful error handling

---

# 18. Contributing

## 18.1 Branch Strategy

Recommended:

```text
main
develop
feature/*
fix/*
```

Example:

```bash
git checkout -b feature/project-risk-engine
```

---

## 18.2 Commit Convention

Use descriptive commits.

Examples:

```text
feat: add project history API
feat: add risk scoring engine
fix: correct progress normalization
docs: update ingestion workflow
test: add project snapshot tests
```

---

## 18.3 Pull Requests

Every pull request should include:

* Description
* Motivation
* Screenshots where relevant
* Tests
* Database migration notes
* API changes
* Breaking changes, if any

---

# 19. License

> **TBD**

Select an appropriate open-source license before the first public release.

Possible options include:

```text
MIT
Apache-2.0
GPL-3.0
```

The final license must reflect the project's ownership, competition rules and any third-party dependencies/data restrictions.

---

# 20. Project Status

## Current Stage

**Architecture / Planning**

The solution architecture has been defined conceptually.

### Completed

* Problem statement understanding
* Target users identified
* Core solution defined
* Data ingestion architecture defined
* Database architecture defined
* Risk engine concept defined
* Dashboard architecture defined
* ML integration approach defined

### Next Development Priorities

```text
1. Extract April/May/June PAIMANA data
2. Build a unified project dataset
3. Analyze project-ID matching
4. Measure missing values
5. Define final database schema
6. Implement ingestion pipeline
7. Build project dashboard
8. Implement analytics
9. Implement rule-based risk engine
10. Evaluate whether sufficient historical data exists for ML
11. Add predictive model
12. Implement early-warning dashboard
13. Add reporting and final polish
```

---

# Final Product Flow

The complete system is intended to operate as follows:

```text
                         ┌──────────────────┐
                         │ PAIMANA REPORTS  │
                         │ PDF / Excel/CSV  │
                         └────────┬─────────┘
                                  ↓
                         ┌──────────────────┐
                         │ DATA INGESTION   │
                         └────────┬─────────┘
                                  ↓
                         ┌──────────────────┐
                         │ CLEAN + VALIDATE │
                         └────────┬─────────┘
                                  ↓
                         ┌──────────────────┐
                         │ PROJECT DATABASE │
                         └────────┬─────────┘
                                  ↓
                   ┌──────────────┼──────────────┐
                   ↓              ↓              ↓
               ANALYTICS      RISK ENGINE     PREDICTION
                   │              │              │
                   └──────────────┼──────────────┘
                                  ↓
                         ┌──────────────────┐
                         │ DECISION ENGINE  │
                         └────────┬─────────┘
                                  ↓
                    ┌──────────────────────────┐
                    │ EARLY WARNING SYSTEM     │
                    └────────────┬─────────────┘
                                 ↓
                    ┌──────────────────────────┐
                    │ MONITORING DASHBOARD     │
                    ├──────────────────────────┤
                    │ Project Health           │
                    │ Risk                     │
                    │ Progress                 │
                    │ Financials               │
                    │ Forecasts                │
                    │ Alerts                   │
                    │ Analytics                │
                    └──────────────────────────┘
```

---

## Core Design Principle

The platform is **not simply an AI model** and it is not simply a dashboard.

It is a complete pipeline:

> **Data → Structure → Monitor → Analyze → Detect → Predict → Warn → Decide**

The monitoring and analytics layers remain useful independently, while the predictive layer can be progressively introduced as the quality and quantity of historical PAIMANA data increases.
