"""
Risk Engine — Service
Orchestrates the full risk assessment pipeline for a project.
Called after each import to recalculate risk and generate alerts.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.models.orm import (
    Alert, AlertSeverity, AlertType, Milestone,
    Project, ProjectSnapshot, RiskAssessment, RiskConfiguration, RiskLevel,
)
from app.risk.config import RiskConfig, DEFAULT_CONFIG
from app.risk.features import compute_features
from app.risk.rules import evaluate_rules
from app.risk.scoring import compute_all_scores
from app.risk.explanations import (
    generate_explanation,
    generate_recommended_action,
    format_alert_description,
)


async def get_active_config(db: AsyncSession) -> RiskConfig:
    """Load the active risk configuration from the database."""
    result = await db.execute(
        select(RiskConfiguration).where(RiskConfiguration.is_active == True).limit(1)
    )
    orm_config = result.scalar_one_or_none()
    if orm_config:
        return RiskConfig.from_orm(orm_config)
    return DEFAULT_CONFIG


async def assess_project(
    db: AsyncSession,
    project: Project,
    snapshot: ProjectSnapshot,
    config: Optional[RiskConfig] = None,
) -> RiskAssessment:
    """
    Compute a complete risk assessment for a project snapshot.
    Persists the RiskAssessment and any triggered Alerts.
    """
    if config is None:
        config = await get_active_config(db)

    # ── Fetch previous snapshot for velocity ─────────────────────────────
    prev_result = await db.execute(
        select(ProjectSnapshot)
        .where(
            ProjectSnapshot.project_id == project.id,
            ProjectSnapshot.report_month < snapshot.report_month,
        )
        .order_by(desc(ProjectSnapshot.report_month))
        .limit(1)
    )
    prev_snapshot = prev_result.scalar_one_or_none()

    # ── Fetch milestones ──────────────────────────────────────────────────
    milestone_result = await db.execute(
        select(Milestone).where(Milestone.project_id == project.id)
    )
    milestones = milestone_result.scalars().all()

    # ── Compute features ──────────────────────────────────────────────────
    features = compute_features(
        physical_progress=float(snapshot.physical_progress) if snapshot.physical_progress else None,
        planned_progress=float(snapshot.planned_progress) if snapshot.planned_progress else None,
        cumulative_expenditure=float(snapshot.cumulative_expenditure) if snapshot.cumulative_expenditure else None,
        current_cost=float(snapshot.current_cost) if snapshot.current_cost else None,
        original_cost=float(project.original_cost) if project.original_cost else None,
        original_start_date=project.original_start_date,
        original_completion_date=project.original_completion_date,
        revised_completion_date=snapshot.current_completion_date or project.revised_completion_date,
        current_date=snapshot.report_month,
        prev_physical_progress=float(prev_snapshot.physical_progress) if prev_snapshot and prev_snapshot.physical_progress else None,
        prev_expenditure=float(prev_snapshot.cumulative_expenditure) if prev_snapshot and prev_snapshot.cumulative_expenditure else None,
        milestones=list(milestones),
    )

    # ── Evaluate rules ────────────────────────────────────────────────────
    rule_results = evaluate_rules(features, config)

    # ── Compute scores ────────────────────────────────────────────────────
    scores = compute_all_scores(features, config)
    overall_health = scores["overall_health"]
    overall_risk: RiskLevel = scores["overall_risk"]

    # ── Generate explanation ──────────────────────────────────────────────
    explanation = generate_explanation(features, rule_results, overall_risk, overall_health)
    recommended_action = generate_recommended_action(rule_results, overall_risk)

    # ── Persist risk assessment ───────────────────────────────────────────
    assessment = RiskAssessment(
        project_id=project.id,
        snapshot_id=snapshot.id,
        financial_health=scores["financial_health"],
        schedule_health=scores["schedule_health"],
        progress_health=scores["progress_health"],
        milestone_health=scores["milestone_health"],
        overall_health=overall_health,
        overall_risk=overall_risk,
        financial_risk=scores["financial_risk"],
        schedule_risk=scores["schedule_risk"],
        progress_risk=scores["progress_risk"],
        progress_gap=features.progress_gap,
        spending_progress_gap=features.spending_progress_gap,
        cost_escalation_pct=features.cost_escalation_pct,
        schedule_escalation_days=features.schedule_escalation_days,
        time_consumed_pct=features.time_consumed_pct,
        expenditure_pct=features.expenditure_pct,
        progress_velocity=features.progress_velocity,
        explanation=explanation,
        config_snapshot=config.to_dict(),
    )
    db.add(assessment)
    await db.flush()  # get assessment.id

    # ── Generate alerts from rule results ─────────────────────────────────
    _SEVERITY_MAP = {
        RiskLevel.critical: AlertSeverity.critical,
        RiskLevel.high: AlertSeverity.high,
        RiskLevel.medium: AlertSeverity.medium,
        RiskLevel.low: AlertSeverity.low,
    }
    _TYPE_MAP = {
        "progress": AlertType.progress_lag,
        "financial": AlertType.cost_overrun,
        "schedule": AlertType.schedule_delay,
        "milestone": AlertType.milestone_missed,
    }

    for rule in rule_results:
        if rule.risk_level in (RiskLevel.medium, RiskLevel.high, RiskLevel.critical):
            alert = Alert(
                project_id=project.id,
                risk_assessment_id=assessment.id,
                alert_type=_TYPE_MAP.get(rule.dimension, AlertType.progress_lag),
                severity=_SEVERITY_MAP[rule.risk_level],
                title=f"{rule.dimension.capitalize()} Risk: {project.project_name[:60]}",
                description=rule.message,
                evidence=rule.evidence,
                recommended_action=recommended_action,
                report_month=snapshot.report_month,
            )
            db.add(alert)

    await db.flush()
    return assessment


async def assess_all_projects_for_month(
    db: AsyncSession,
    report_month: date,
) -> dict:
    """
    Run risk assessment for all projects that have a snapshot for the given month.
    Returns summary statistics.
    """
    config = await get_active_config(db)

    result = await db.execute(
        select(ProjectSnapshot).where(ProjectSnapshot.report_month == report_month)
    )
    snapshots = result.scalars().all()

    assessed = 0
    errors = 0

    for snapshot in snapshots:
        proj_result = await db.execute(
            select(Project).where(Project.id == snapshot.project_id)
        )
        project = proj_result.scalar_one_or_none()
        if not project:
            continue
        try:
            await assess_project(db, project, snapshot, config)
            assessed += 1
        except Exception as e:
            errors += 1

    return {
        "report_month": str(report_month),
        "snapshots_found": len(snapshots),
        "assessed": assessed,
        "errors": errors,
    }
