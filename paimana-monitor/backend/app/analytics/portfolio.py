"""
Analytics — Portfolio Aggregations
Server-side computation of dashboard summary statistics.
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import func, select, and_, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import (
    Alert, AlertSeverity, Project, ProjectSnapshot,
    RiskAssessment, RiskLevel,
)


async def get_portfolio_summary(db: AsyncSession) -> dict:
    """Aggregate portfolio-level KPIs from the database."""
    # Project counts by risk
    result = await db.execute(
        select(
            func.count(RiskAssessment.id).label("total"),
            func.count(case((RiskAssessment.overall_risk == RiskLevel.low, 1))).label("low"),
            func.count(case((RiskAssessment.overall_risk == RiskLevel.medium, 1))).label("medium"),
            func.count(case((RiskAssessment.overall_risk == RiskLevel.high, 1))).label("high"),
            func.count(case((RiskAssessment.overall_risk == RiskLevel.critical, 1))).label("critical"),
            func.avg(RiskAssessment.overall_health).label("avg_health"),
        ).select_from(
            # Only latest risk per project
            select(RiskAssessment).distinct(RiskAssessment.project_id).order_by(
                RiskAssessment.project_id, RiskAssessment.created_at.desc()
            ).subquery()
        )
    )
    risk_row = result.one()

    # Financial totals from projects table
    fin_result = await db.execute(
        select(
            func.count(Project.id).label("total_projects"),
            func.sum(Project.original_cost).label("total_original_cost"),
            func.sum(Project.revised_cost).label("total_revised_cost"),
        )
    )
    fin_row = fin_result.one()

    # Total expenditure from latest snapshots
    exp_result = await db.execute(
        select(func.sum(ProjectSnapshot.cumulative_expenditure)).select_from(
            select(ProjectSnapshot).distinct(ProjectSnapshot.project_id).order_by(
                ProjectSnapshot.project_id, ProjectSnapshot.report_month.desc()
            ).subquery()
        )
    )
    total_exp = exp_result.scalar()

    # Stalled count
    stalled_result = await db.execute(
        select(func.count(Project.id)).where(Project.current_status == "stalled")
    )
    stalled_count = stalled_result.scalar() or 0

    # Active alerts
    alert_result = await db.execute(
        select(
            func.count(Alert.id).label("total"),
            func.count(case((Alert.severity == AlertSeverity.critical, 1))).label("critical"),
            func.count(case((Alert.severity == AlertSeverity.high, 1))).label("high"),
            func.count(case((Alert.severity == AlertSeverity.medium, 1))).label("medium"),
        ).where(Alert.is_resolved == False)
    )
    alert_row = alert_result.one()

    return {
        "total_projects": fin_row.total_projects or 0,
        "low_risk_count": risk_row.low or 0,
        "medium_risk_count": risk_row.medium or 0,
        "high_risk_count": risk_row.high or 0,
        "critical_risk_count": risk_row.critical or 0,
        "avg_health_score": round(float(risk_row.avg_health or 0), 1),
        "total_original_cost": float(fin_row.total_original_cost or 0),
        "total_revised_cost": float(fin_row.total_revised_cost or 0),
        "total_expenditure": float(total_exp or 0),
        "stalled_count": stalled_count,
        "active_alerts": {
            "total": alert_row.total or 0,
            "critical": alert_row.critical or 0,
            "high": alert_row.high or 0,
            "medium": alert_row.medium or 0,
        },
    }


async def get_sector_stats(db: AsyncSession) -> list[dict]:
    """Per-sector aggregations for dashboard charts."""
    result = await db.execute(
        select(
            Project.sector,
            func.count(Project.id).label("project_count"),
            func.sum(Project.original_cost).label("total_cost"),
            func.sum(Project.revised_cost).label("total_revised_cost"),
        )
        .where(Project.sector != None)
        .group_by(Project.sector)
        .order_by(func.count(Project.id).desc())
    )
    rows = result.all()

    # Add average health per sector from latest risk assessments
    stats = []
    for row in rows:
        health_result = await db.execute(
            select(func.avg(RiskAssessment.overall_health)).select_from(
                select(RiskAssessment).join(Project).distinct(RiskAssessment.project_id).where(
                    Project.sector == row.sector
                ).order_by(RiskAssessment.project_id, RiskAssessment.created_at.desc()).subquery()
            )
        )
        avg_health = health_result.scalar()

        high_risk = await db.execute(
            select(func.count()).select_from(
                select(RiskAssessment).join(Project).distinct(RiskAssessment.project_id).where(
                    Project.sector == row.sector,
                    RiskAssessment.overall_risk.in_([RiskLevel.high, RiskLevel.critical])
                ).order_by(RiskAssessment.project_id, RiskAssessment.created_at.desc()).subquery()
            )
        )

        stats.append({
            "sector": row.sector,
            "project_count": row.project_count,
            "total_cost": float(row.total_cost or 0),
            "total_revised_cost": float(row.total_revised_cost or 0),
            "avg_health": round(float(avg_health or 50), 1),
            "high_risk_count": high_risk.scalar() or 0,
        })
    return stats


async def get_state_stats(db: AsyncSession) -> list[dict]:
    """Per-state aggregations."""
    result = await db.execute(
        select(
            Project.state,
            func.count(Project.id).label("project_count"),
        )
        .where(Project.state != None)
        .group_by(Project.state)
        .order_by(func.count(Project.id).desc())
        .limit(20)
    )
    rows = result.all()
    stats = []
    for row in rows:
        high_risk = await db.execute(
            select(func.count()).select_from(
                select(RiskAssessment).join(Project).distinct(RiskAssessment.project_id).where(
                    Project.state == row.state,
                    RiskAssessment.overall_risk.in_([RiskLevel.high, RiskLevel.critical])
                ).order_by(RiskAssessment.project_id, RiskAssessment.created_at.desc()).subquery()
            )
        )
        stats.append({
            "state": row.state,
            "project_count": row.project_count,
            "high_risk_count": high_risk.scalar() or 0,
        })
    return stats


async def get_risk_distribution(db: AsyncSession) -> dict:
    """Risk level distribution across portfolio."""
    result = await db.execute(
        select(
            RiskAssessment.overall_risk,
            func.count(RiskAssessment.id).label("count"),
        ).select_from(
            select(RiskAssessment).distinct(RiskAssessment.project_id).order_by(
                RiskAssessment.project_id, RiskAssessment.created_at.desc()
            ).subquery()
        ).group_by(RiskAssessment.overall_risk)
    )
    distribution = {row.overall_risk.value: row.count for row in result.all()}
    return {
        "low": distribution.get("low", 0),
        "medium": distribution.get("medium", 0),
        "high": distribution.get("high", 0),
        "critical": distribution.get("critical", 0),
    }
