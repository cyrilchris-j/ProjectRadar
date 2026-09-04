"""
Projects API — list, detail, history, forecast.
"""
from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.auth import get_current_user, require_roles
from app.analytics.forecasting import forecast_project
from app.database.connection import get_db
from app.models.orm import (
    Alert, Milestone, Project, ProjectSnapshot,
    RiskAssessment, User, UserRole,
)
from app.schemas.schemas import (
    AlertOut, ForecastOut, MilestoneOut, PaginatedResponse,
    PaginationMeta, ProjectDetail, ProjectListItem,
    RiskAssessmentOut, SnapshotOut,
)

router = APIRouter(prefix="/api/projects", tags=["projects"])

_VIEWER_ROLES = (UserRole.admin, UserRole.analyst, UserRole.officer, UserRole.viewer)


@router.get("", response_model=PaginatedResponse)
async def list_projects(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sector: Optional[str] = None,
    state: Optional[str] = None,
    ministry: Optional[str] = None,
    risk: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(*_VIEWER_ROLES)),
):
    """
    Paginated, server-side filtered project list.
    Joins latest snapshot and latest risk for each project.
    """
    # Build base query
    q = select(Project)

    if sector:
        q = q.where(Project.sector == sector)
    if state:
        q = q.where(Project.state == state)
    if ministry:
        q = q.where(Project.ministry == ministry)
    if status:
        q = q.where(Project.current_status == status)
    if search:
        q = q.where(Project.project_name.ilike(f"%{search}%"))

    # Total count
    count_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = count_result.scalar()

    # Paginate
    q = q.offset((page - 1) * limit).limit(limit).order_by(Project.project_name)
    result = await db.execute(q)
    projects = result.scalars().all()

    items = []
    for project in projects:
        # Latest snapshot
        snap_result = await db.execute(
            select(ProjectSnapshot)
            .where(ProjectSnapshot.project_id == project.id)
            .order_by(desc(ProjectSnapshot.report_month))
            .limit(1)
        )
        snap = snap_result.scalar_one_or_none()

        # Latest risk
        risk_result = await db.execute(
            select(RiskAssessment)
            .where(RiskAssessment.project_id == project.id)
            .order_by(desc(RiskAssessment.created_at))
            .limit(1)
        )
        ra = risk_result.scalar_one_or_none()

        # Filter by risk level if requested
        if risk and (ra is None or ra.overall_risk.value != risk.lower()):
            continue

        item = ProjectListItem(
            id=project.id,
            project_id=project.project_id,
            project_name=project.project_name,
            ministry=project.ministry,
            sector=project.sector,
            state=project.state,
            current_status=project.current_status,
            original_cost=float(project.original_cost) if project.original_cost else None,
            revised_cost=float(project.revised_cost) if project.revised_cost else None,
            physical_progress=float(snap.physical_progress) if snap and snap.physical_progress else None,
            cumulative_expenditure=float(snap.cumulative_expenditure) if snap and snap.cumulative_expenditure else None,
            report_month=snap.report_month if snap else None,
            overall_risk=ra.overall_risk if ra else None,
            overall_health=float(ra.overall_health) if ra and ra.overall_health else None,
        )
        items.append(item)

    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(
            page=page, limit=limit, total=total,
            total_pages=max(1, -(-total // limit)),
        ),
    )


@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(*_VIEWER_ROLES)),
):
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.snapshots), selectinload(Project.milestones))
        .where(Project.project_id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail=f"Project '{project_id}' not found")

    # Latest risk
    risk_result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.project_id == project.id)
        .order_by(desc(RiskAssessment.created_at))
        .limit(1)
    )
    latest_risk = risk_result.scalar_one_or_none()

    # Active alerts
    alert_result = await db.execute(
        select(Alert)
        .where(Alert.project_id == project.id, Alert.is_resolved == False)
        .order_by(desc(Alert.created_at))
        .limit(10)
    )
    alerts = alert_result.scalars().all()

    return ProjectDetail(
        **{k: v for k, v in project.__dict__.items() if not k.startswith("_")},
        snapshots=[SnapshotOut.model_validate(s) for s in project.snapshots],
        milestones=[MilestoneOut.model_validate(m) for m in project.milestones],
        latest_risk=RiskAssessmentOut.model_validate(latest_risk) if latest_risk else None,
        active_alerts=[AlertOut.model_validate(a) for a in alerts],
    )


@router.get("/{project_id}/history", response_model=list[SnapshotOut])
async def get_project_history(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(*_VIEWER_ROLES)),
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    snaps_result = await db.execute(
        select(ProjectSnapshot)
        .where(ProjectSnapshot.project_id == project.id)
        .order_by(ProjectSnapshot.report_month)
    )
    return [SnapshotOut.model_validate(s) for s in snaps_result.scalars().all()]


@router.get("/{project_id}/forecast", response_model=ForecastOut)
async def get_project_forecast(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(*_VIEWER_ROLES)),
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    snaps_result = await db.execute(
        select(ProjectSnapshot)
        .where(ProjectSnapshot.project_id == project.id)
        .order_by(ProjectSnapshot.report_month)
    )
    snapshots = [
        {
            "report_month": s.report_month,
            "physical_progress": float(s.physical_progress) if s.physical_progress else None,
            "cumulative_expenditure": float(s.cumulative_expenditure) if s.cumulative_expenditure else None,
        }
        for s in snaps_result.scalars().all()
    ]

    forecast = forecast_project(
        snapshots=snapshots,
        original_completion_date=project.original_completion_date,
        original_cost=float(project.original_cost) if project.original_cost else None,
    )

    return ForecastOut(
        project_id=project.id,
        forecast_completion_date=forecast.forecast_completion_date,
        forecast_progress_next_month=forecast.forecast_progress_next_month,
        forecast_expenditure_next_month=forecast.forecast_expenditure_next_month,
        expected_delay_days=forecast.expected_delay_days,
        method_used=forecast.method_used,
        confidence_note=forecast.confidence_note,
    )


@router.get("/{project_id}/risk", response_model=RiskAssessmentOut)
async def get_project_risk(
    project_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(*_VIEWER_ROLES)),
):
    result = await db.execute(select(Project).where(Project.project_id == project_id))
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    risk_result = await db.execute(
        select(RiskAssessment)
        .where(RiskAssessment.project_id == project.id)
        .order_by(desc(RiskAssessment.created_at))
        .limit(1)
    )
    ra = risk_result.scalar_one_or_none()
    if not ra:
        raise HTTPException(status_code=404, detail="No risk assessment available yet")
    return RiskAssessmentOut.model_validate(ra)
