"""
Admin API — user management, risk config, audit logs.
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from passlib.context import CryptContext
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user, hash_password, require_roles
from app.database.connection import get_db
from app.models.orm import AuditLog, RiskConfiguration, User, UserRole
from app.schemas.schemas import (
    RiskConfigOut, RiskConfigUpdate, UserCreate, UserOut,
)

router = APIRouter(prefix="/api/admin", tags=["admin"])


# ─── Users ────────────────────────────────────────────────────────────────────

@router.get("/users", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    result = await db.execute(select(User).order_by(User.full_name))
    return [UserOut.model_validate(u) for u in result.scalars().all()]


@router.post("/users", response_model=UserOut, status_code=201)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    # Check duplicate email
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        full_name=body.full_name,
        password_hash=hash_password(body.password),
        role=body.role,
    )
    db.add(user)
    db.add(AuditLog(
        user_id=current_user.id,
        action="create_user",
        entity_type="user",
        entity_id=str(user.id),
        metadata={"email": body.email, "role": body.role.value},
    ))
    await db.flush()
    return UserOut.model_validate(user)


@router.patch("/users/{user_id}/deactivate")
async def deactivate_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    user.is_active = False
    db.add(AuditLog(user_id=current_user.id, action="deactivate_user", entity_type="user", entity_id=str(user_id)))
    return {"status": "deactivated"}


# ─── Risk Configuration ────────────────────────────────────────────────────────

@router.get("/risk-config", response_model=RiskConfigOut)
async def get_risk_config(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.analyst)),
):
    result = await db.execute(
        select(RiskConfiguration).where(RiskConfiguration.is_active == True).limit(1)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="No active risk configuration found")
    return RiskConfigOut.model_validate(config)


@router.patch("/risk-config", response_model=RiskConfigOut)
async def update_risk_config(
    body: RiskConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    result = await db.execute(
        select(RiskConfiguration).where(RiskConfiguration.is_active == True).limit(1)
    )
    config = result.scalar_one_or_none()
    if not config:
        raise HTTPException(status_code=404, detail="No active risk configuration found")

    update_data = body.model_dump(exclude_none=True)

    # Validate weight sum if any weights are updated
    weight_fields = {"financial_weight", "schedule_weight", "progress_weight", "milestone_weight"}
    if any(k in update_data for k in weight_fields):
        new_weights = {
            "financial_weight": update_data.get("financial_weight", float(config.financial_weight)),
            "schedule_weight": update_data.get("schedule_weight", float(config.schedule_weight)),
            "progress_weight": update_data.get("progress_weight", float(config.progress_weight)),
            "milestone_weight": update_data.get("milestone_weight", float(config.milestone_weight)),
        }
        total = sum(new_weights.values())
        if abs(total - 1.0) > 0.01:
            raise HTTPException(
                status_code=400,
                detail=f"Weights must sum to 1.0 (current sum: {total:.3f})",
            )

    for key, value in update_data.items():
        setattr(config, key, value)
    config.updated_by = current_user.id

    db.add(AuditLog(
        user_id=current_user.id,
        action="update_risk_config",
        entity_type="risk_configuration",
        entity_id=str(config.id),
        metadata=update_data,
    ))
    await db.flush()
    return RiskConfigOut.model_validate(config)


# ─── Audit Logs ───────────────────────────────────────────────────────────────

@router.get("/audit-logs")
async def get_audit_logs(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
    action: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin)),
):
    q = select(AuditLog)
    if action:
        q = q.where(AuditLog.action == action)
    q = q.order_by(desc(AuditLog.created_at)).offset((page - 1) * limit).limit(limit)
    result = await db.execute(q)
    logs = result.scalars().all()
    return [
        {
            "id": str(log.id),
            "user_id": str(log.user_id) if log.user_id else None,
            "action": log.action,
            "entity_type": log.entity_type,
            "entity_id": log.entity_id,
            "metadata": log.metadata,
            "created_at": log.created_at.isoformat(),
        }
        for log in logs
    ]
