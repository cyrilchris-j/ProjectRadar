"""
Risk Engine — Health Scoring
Computes dimension scores and overall weighted health score from features.
Health scores are 0–100 where 100 = perfectly healthy.
"""
from __future__ import annotations

from typing import Optional
from app.risk.config import RiskConfig
from app.risk.features import ProjectFeatures
from app.risk.rules import RuleResult
from app.models.orm import RiskLevel


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def compute_progress_health(features: ProjectFeatures, config: RiskConfig) -> Optional[float]:
    """
    Progress health: penalizes falling behind planned progress.
    Starts at 100, reduced proportionally to the gap magnitude.
    """
    if features.progress_gap is None:
        return None
    gap = features.progress_gap
    if gap >= 0:
        # Slightly ahead or on track
        return _clamp(100.0 + gap * 0.3)
    # Behind: penalty scales with gap
    penalty = abs(gap) * 3.5
    return _clamp(100.0 - penalty)


def compute_financial_health(features: ProjectFeatures, config: RiskConfig) -> Optional[float]:
    """
    Financial health: penalizes cost escalation and expenditure outpacing progress.
    """
    score = 100.0
    has_data = False

    if features.cost_escalation_pct is not None:
        has_data = True
        if features.cost_escalation_pct > 0:
            score -= min(features.cost_escalation_pct * 1.2, 40)

    if features.spending_progress_gap is not None:
        has_data = True
        if features.spending_progress_gap > 0:
            score -= min(features.spending_progress_gap * 1.5, 40)

    return _clamp(score) if has_data else None


def compute_schedule_health(features: ProjectFeatures, config: RiskConfig) -> Optional[float]:
    """
    Schedule health: penalizes delay in completion date and being past deadline.
    """
    score = 100.0
    has_data = False

    if features.schedule_escalation_days is not None:
        has_data = True
        if features.schedule_escalation_days > 0:
            score -= min(features.schedule_escalation_days / config.schedule_delay_high_days * 60, 60)

    if features.is_past_original_deadline and features.days_overdue:
        has_data = True
        score -= min(features.days_overdue / 30 * 5, 40)

    return _clamp(score) if has_data else None


def compute_milestone_health(features: ProjectFeatures, config: RiskConfig) -> Optional[float]:
    """
    Milestone health: based on completion ratio vs time consumed, plus missed/delayed penalties.
    """
    if features.total_milestones == 0:
        return None

    score = 100.0
    if features.missed_milestones > 0:
        score -= features.missed_milestones * 15
    if features.delayed_milestones > 0:
        score -= features.delayed_milestones * 8
    if features.milestone_completion_ratio is not None and features.time_consumed_pct is not None:
        expected = features.time_consumed_pct / 100
        actual = features.milestone_completion_ratio
        if actual < expected:
            shortfall = (expected - actual) * 100
            score -= shortfall * 0.8

    return _clamp(score)


def risk_level_from_health(health: float, config: RiskConfig) -> RiskLevel:
    """Map overall health score to a risk level using configured thresholds."""
    if health >= config.health_low_threshold:
        return RiskLevel.low
    elif health >= config.health_medium_threshold:
        return RiskLevel.medium
    elif health >= config.health_critical_threshold:
        return RiskLevel.high
    else:
        return RiskLevel.critical


def dimension_risk(score: Optional[float], config: RiskConfig) -> RiskLevel:
    """Map a dimension health score to its risk level."""
    if score is None:
        return RiskLevel.low
    return risk_level_from_health(score, config)


def compute_overall_health(
    financial_health: Optional[float],
    schedule_health: Optional[float],
    progress_health: Optional[float],
    milestone_health: Optional[float],
    config: RiskConfig,
) -> float:
    """
    Weighted average of available dimension health scores.
    Adjusts weights dynamically when dimensions have no data.
    """
    dimensions = [
        (financial_health, config.financial_weight),
        (schedule_health, config.schedule_weight),
        (progress_health, config.progress_weight),
        (milestone_health, config.milestone_weight),
    ]
    available = [(score, weight) for score, weight in dimensions if score is not None]
    if not available:
        return 50.0  # neutral default when no data
    total_weight = sum(w for _, w in available)
    weighted_sum = sum(score * weight for score, weight in available)
    return _clamp(round(weighted_sum / total_weight, 2))


def compute_all_scores(
    features: ProjectFeatures,
    config: RiskConfig,
) -> dict:
    """
    Compute all health scores and risk levels for a project.
    Returns a dict suitable for creating a RiskAssessment record.
    """
    financial_health = compute_financial_health(features, config)
    schedule_health = compute_schedule_health(features, config)
    progress_health = compute_progress_health(features, config)
    milestone_health = compute_milestone_health(features, config)
    overall_health = compute_overall_health(
        financial_health, schedule_health, progress_health, milestone_health, config
    )

    return {
        "financial_health": financial_health,
        "schedule_health": schedule_health,
        "progress_health": progress_health,
        "milestone_health": milestone_health,
        "overall_health": overall_health,
        "overall_risk": risk_level_from_health(overall_health, config),
        "financial_risk": dimension_risk(financial_health, config),
        "schedule_risk": dimension_risk(schedule_health, config),
        "progress_risk": dimension_risk(progress_health, config),
    }
