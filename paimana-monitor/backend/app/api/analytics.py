"""
Analytics API — Portfolio dashboard, sector/state stats, risk distribution.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user, require_roles
from app.analytics.portfolio import (
    get_portfolio_summary, get_risk_distribution,
    get_sector_stats, get_state_stats,
)
from app.database.connection import get_db
from app.models.orm import User, UserRole
from app.schemas.schemas import PortfolioSummary

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

_VIEWER_ROLES = (UserRole.admin, UserRole.analyst, UserRole.officer, UserRole.viewer)


@router.get("/portfolio", response_model=dict)
async def portfolio_summary(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(*_VIEWER_ROLES)),
):
    """Main dashboard KPIs."""
    return await get_portfolio_summary(db)


@router.get("/sectors")
async def sector_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(*_VIEWER_ROLES)),
):
    return await get_sector_stats(db)


@router.get("/states")
async def state_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(*_VIEWER_ROLES)),
):
    return await get_state_stats(db)


@router.get("/risk-distribution")
async def risk_distribution(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(*_VIEWER_ROLES)),
):
    return await get_risk_distribution(db)
