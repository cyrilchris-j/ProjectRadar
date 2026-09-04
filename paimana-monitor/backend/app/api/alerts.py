"""
Alerts API — list, filter, resolve.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user, require_roles
from app.database.connection import get_db
from app.models.orm import Alert, AlertSeverity, AuditLog, Project, User, UserRole
from app.schemas.schemas import AlertOut, AlertResolve, PaginatedResponse, PaginationMeta
from datetime import datetime

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=PaginatedResponse)
async def list_alerts(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    severity: Optional[str] = None,
    alert_type: Optional[str] = None,
    is_resolved: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.admin, UserRole.analyst, UserRole.officer, UserRole.viewer
    )),
):
    q = select(Alert).where(Alert.is_resolved == is_resolved)
    if severity:
        q = q.where(Alert.severity == severity.lower())
    if alert_type:
        q = q.where(Alert.alert_type == alert_type.lower())

    count_result = await db.execute(select(func.count()).select_from(q.subquery()))
    total = count_result.scalar()

    q = q.order_by(
        desc(Alert.severity),
        desc(Alert.created_at),
    ).offset((page - 1) * limit).limit(limit)
    result = await db.execute(q)
    alerts = result.scalars().all()

    # Attach project names
    items = []
    for alert in alerts:
        proj_result = await db.execute(select(Project).where(Project.id == alert.project_id))
        project = proj_result.scalar_one_or_none()
        data = AlertOut.model_validate(alert)
        data.project_name = project.project_name if project else None
        items.append(data)

    return PaginatedResponse(
        data=items,
        pagination=PaginationMeta(page=page, limit=limit, total=total, total_pages=max(1, -(-total // limit))),
    )


@router.get("/summary")
async def alerts_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(
        UserRole.admin, UserRole.analyst, UserRole.officer, UserRole.viewer
    )),
):
    """Count of active alerts by severity."""
    from sqlalchemy import case
    result = await db.execute(
        select(
            func.count(Alert.id).label("total"),
            func.count(Alert.id).filter(Alert.severity == AlertSeverity.critical).label("critical"),
            func.count(Alert.id).filter(Alert.severity == AlertSeverity.high).label("high"),
            func.count(Alert.id).filter(Alert.severity == AlertSeverity.medium).label("medium"),
            func.count(Alert.id).filter(Alert.severity == AlertSeverity.low).label("low"),
        ).where(Alert.is_resolved == False)
    )
    row = result.one()
    return {"total": row.total, "critical": row.critical, "high": row.high, "medium": row.medium, "low": row.low}


@router.patch("/{alert_id}/resolve")
async def resolve_alert(
    alert_id: UUID,
    body: AlertResolve,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.officer)),
):
    result = await db.execute(select(Alert).where(Alert.id == alert_id))
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    if alert.is_resolved:
        raise HTTPException(status_code=400, detail="Alert is already resolved")

    alert.is_resolved = True
    alert.resolved_by = current_user.id
    alert.resolved_at = datetime.utcnow()
    alert.resolution_note = body.resolution_note

    db.add(AuditLog(
        user_id=current_user.id,
        action="resolve_alert",
        entity_type="alert",
        entity_id=str(alert_id),
        metadata_={"resolution_note": body.resolution_note},
    ))
    return {"status": "resolved", "alert_id": str(alert_id)}
