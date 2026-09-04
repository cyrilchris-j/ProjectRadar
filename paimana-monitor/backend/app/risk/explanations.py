"""
Risk Engine — Explanation Generator
Converts raw RuleResults and feature data into human-readable explanations.
Every risk assessment MUST have an explanation. No unexplained scores.
"""
from __future__ import annotations

from app.risk.rules import RuleResult
from app.risk.features import ProjectFeatures
from app.models.orm import RiskLevel


def generate_explanation(
    features: ProjectFeatures,
    rule_results: list[RuleResult],
    overall_risk: RiskLevel,
    overall_health: float,
) -> list[str]:
    """
    Produce an ordered list of human-readable explanation strings.
    Ordered by severity (high → medium → low → informational).
    """
    explanations: list[str] = []

    # Add rule-based explanations (sorted by severity)
    severity_order = {RiskLevel.critical: 0, RiskLevel.high: 1, RiskLevel.medium: 2, RiskLevel.low: 3}
    sorted_rules = sorted(rule_results, key=lambda r: severity_order.get(r.risk_level, 3))
    for rule in sorted_rules:
        explanations.append(rule.message)

    # Add informational context when no risk rules fired
    if not rule_results:
        if overall_health >= 75:
            explanations.append("Project is progressing within acceptable parameters.")
        else:
            explanations.append("Insufficient data to evaluate all risk dimensions.")

    return explanations


def generate_recommended_action(
    rule_results: list[RuleResult],
    overall_risk: RiskLevel,
) -> str:
    """Produce a recommended action string based on the detected risk conditions."""
    if not rule_results:
        return "No immediate action required. Continue regular monitoring."

    dimensions = {r.dimension for r in rule_results}
    actions = []

    if "progress" in dimensions:
        actions.append("review implementation schedule and identify bottlenecks")
    if "financial" in dimensions:
        actions.append("audit expenditure against physical deliverables")
    if "schedule" in dimensions:
        actions.append("assess revised completion feasibility and update project schedule")
    if "milestone" in dimensions:
        actions.append("escalate missed milestones to implementing agency for corrective action")

    if overall_risk in (RiskLevel.critical, RiskLevel.high):
        actions.append("flag for ministerial-level review")

    return "Recommended: " + "; ".join(actions).capitalize() + "."


def format_alert_description(
    rule_results: list[RuleResult],
    features: ProjectFeatures,
) -> str:
    """Format a concise alert description from fired rules."""
    if not rule_results:
        return "Risk assessment completed with no specific rule violations detected."

    lines = ["Risk factors detected:"]
    for rule in rule_results[:5]:  # cap at 5 for readability
        lines.append(f"• {rule.message}")
    if len(rule_results) > 5:
        lines.append(f"• ... and {len(rule_results) - 5} more indicator(s).")

    return "\n".join(lines)
