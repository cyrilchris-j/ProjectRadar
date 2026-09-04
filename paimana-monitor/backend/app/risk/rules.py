"""
Risk Engine — Rule-Based Rules
Deterministic, transparent business rules that flag risk conditions.
Every rule returns a RuleResult with evidence attached.
Rules are not hard-coded throughout the app — all thresholds come from RiskConfig.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.risk.config import RiskConfig
from app.risk.features import ProjectFeatures
from app.models.orm import RiskLevel


@dataclass
class RuleResult:
    """A single fired rule with its evidence."""
    rule_id: str
    dimension: str          # financial | schedule | progress | milestone
    risk_level: RiskLevel
    message: str
    evidence: dict = field(default_factory=dict)


def evaluate_rules(
    features: ProjectFeatures,
    config: RiskConfig,
) -> list[RuleResult]:
    """
    Evaluate all deterministic risk rules against computed features.
    Returns list of fired RuleResults (only rules that detected an issue).
    """
    results: list[RuleResult] = []

    # ── R01: Progress lag (behind planned) ────────────────────────────────
    if features.progress_gap is not None:
        gap = features.progress_gap
        if gap <= config.progress_gap_high:
            results.append(RuleResult(
                rule_id="R01_PROGRESS_HIGH",
                dimension="progress",
                risk_level=RiskLevel.high,
                message=f"Physical progress is {abs(gap):.1f}% below expected level (threshold: {abs(config.progress_gap_high):.0f}%)",
                evidence={
                    "actual_progress": features.physical_progress,
                    "planned_progress": features.planned_progress,
                    "progress_gap": gap,
                    "threshold": config.progress_gap_high,
                },
            ))
        elif gap <= config.progress_gap_warning:
            results.append(RuleResult(
                rule_id="R01_PROGRESS_WARNING",
                dimension="progress",
                risk_level=RiskLevel.medium,
                message=f"Physical progress is {abs(gap):.1f}% below expected level",
                evidence={
                    "actual_progress": features.physical_progress,
                    "planned_progress": features.planned_progress,
                    "progress_gap": gap,
                    "threshold": config.progress_gap_warning,
                },
            ))

    # ── R02: Expenditure ahead of progress ────────────────────────────────
    if features.spending_progress_gap is not None:
        spg = features.spending_progress_gap
        if spg >= config.spending_progress_gap_high:
            results.append(RuleResult(
                rule_id="R02_SPENDING_HIGH",
                dimension="financial",
                risk_level=RiskLevel.high,
                message=f"Expenditure ({features.expenditure_pct:.1f}%) is {spg:.1f}% ahead of physical progress — possible financial inefficiency",
                evidence={
                    "expenditure_pct": features.expenditure_pct,
                    "physical_progress": features.physical_progress,
                    "spending_progress_gap": spg,
                    "threshold": config.spending_progress_gap_high,
                },
            ))
        elif spg >= config.spending_progress_gap_warning:
            results.append(RuleResult(
                rule_id="R02_SPENDING_WARNING",
                dimension="financial",
                risk_level=RiskLevel.medium,
                message=f"Expenditure is {spg:.1f}% ahead of physical progress",
                evidence={
                    "expenditure_pct": features.expenditure_pct,
                    "physical_progress": features.physical_progress,
                    "spending_progress_gap": spg,
                    "threshold": config.spending_progress_gap_warning,
                },
            ))

    # ── R03: Cost escalation ──────────────────────────────────────────────
    if features.cost_escalation_pct is not None:
        esc = features.cost_escalation_pct
        if esc >= config.cost_escalation_high_pct:
            results.append(RuleResult(
                rule_id="R03_COST_ESC_HIGH",
                dimension="financial",
                risk_level=RiskLevel.high,
                message=f"Project cost has escalated by {esc:.1f}% over original estimate",
                evidence={
                    "cost_escalation_pct": esc,
                    "threshold": config.cost_escalation_high_pct,
                },
            ))
        elif esc >= config.cost_escalation_warning_pct:
            results.append(RuleResult(
                rule_id="R03_COST_ESC_WARNING",
                dimension="financial",
                risk_level=RiskLevel.medium,
                message=f"Project cost has escalated by {esc:.1f}% over original estimate",
                evidence={
                    "cost_escalation_pct": esc,
                    "threshold": config.cost_escalation_warning_pct,
                },
            ))

    # ── R04: Schedule escalation ──────────────────────────────────────────
    if features.schedule_escalation_days is not None:
        days = features.schedule_escalation_days
        if days >= config.schedule_delay_high_days:
            results.append(RuleResult(
                rule_id="R04_SCHEDULE_HIGH",
                dimension="schedule",
                risk_level=RiskLevel.high,
                message=f"Completion date has been revised by {days} days ({days // 30} months) beyond original schedule",
                evidence={
                    "schedule_escalation_days": days,
                    "threshold": config.schedule_delay_high_days,
                },
            ))
        elif days >= config.schedule_delay_warning_days:
            results.append(RuleResult(
                rule_id="R04_SCHEDULE_WARNING",
                dimension="schedule",
                risk_level=RiskLevel.medium,
                message=f"Completion date has been revised by {days} days beyond original schedule",
                evidence={
                    "schedule_escalation_days": days,
                    "threshold": config.schedule_delay_warning_days,
                },
            ))

    # ── R05: Past original deadline ───────────────────────────────────────
    if features.is_past_original_deadline and features.physical_progress is not None and features.physical_progress < 100:
        results.append(RuleResult(
            rule_id="R05_PAST_DEADLINE",
            dimension="schedule",
            risk_level=RiskLevel.high,
            message=f"Project is {features.days_overdue} days past original completion deadline with {features.physical_progress:.1f}% progress",
            evidence={
                "days_overdue": features.days_overdue,
                "physical_progress": features.physical_progress,
            },
        ))

    # ── R06: Stalled progress ─────────────────────────────────────────────
    if (
        features.progress_velocity is not None
        and features.progress_velocity <= 0.5
        and features.physical_progress is not None
        and features.physical_progress < 95
    ):
        results.append(RuleResult(
            rule_id="R06_STALLED",
            dimension="progress",
            risk_level=RiskLevel.medium,
            message=f"Project progress has not advanced meaningfully (velocity: {features.progress_velocity:.1f}% last month)",
            evidence={
                "progress_velocity": features.progress_velocity,
                "physical_progress": features.physical_progress,
            },
        ))

    # ── R07: Missed milestones ────────────────────────────────────────────
    if features.missed_milestones > 0:
        results.append(RuleResult(
            rule_id="R07_MILESTONES",
            dimension="milestone",
            risk_level=RiskLevel.high if features.missed_milestones >= 2 else RiskLevel.medium,
            message=f"{features.missed_milestones} milestone(s) missed, {features.delayed_milestones} delayed",
            evidence={
                "missed_milestones": features.missed_milestones,
                "delayed_milestones": features.delayed_milestones,
                "total_milestones": features.total_milestones,
            },
        ))

    # ── R08: Low milestone completion ratio ───────────────────────────────
    if (
        features.milestone_completion_ratio is not None
        and features.total_milestones >= 3
        and features.time_consumed_pct is not None
        and features.time_consumed_pct > 50
    ):
        expected_ratio = features.time_consumed_pct / 100
        actual_ratio = features.milestone_completion_ratio
        if actual_ratio < expected_ratio * 0.6:
            results.append(RuleResult(
                rule_id="R08_MILESTONE_RATIO",
                dimension="milestone",
                risk_level=RiskLevel.medium,
                message=f"Only {actual_ratio*100:.0f}% of milestones complete with {features.time_consumed_pct:.0f}% of project time elapsed",
                evidence={
                    "milestone_completion_ratio": actual_ratio,
                    "time_consumed_pct": features.time_consumed_pct,
                    "total_milestones": features.total_milestones,
                },
            ))

    return results
