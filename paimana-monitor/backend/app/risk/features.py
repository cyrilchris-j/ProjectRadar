"""
Risk Engine — Feature Engineering
Computes derived metrics from project snapshots for health scoring and risk detection.
All functions are pure (no side effects) and handle missing data gracefully.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class ProjectFeatures:
    """
    Derived features for a single project at a single reporting period.
    All optional fields default to None when data is insufficient.
    """
    # ── Time features ──────────────────────────────────────────────────────
    time_consumed_pct: Optional[float] = None      # elapsed / planned_duration * 100
    days_to_original_deadline: Optional[int] = None
    days_overdue: Optional[int] = None             # if past original deadline

    # ── Progress features ──────────────────────────────────────────────────
    physical_progress: Optional[float] = None
    planned_progress: Optional[float] = None
    progress_gap: Optional[float] = None           # actual - planned (negative = behind)
    progress_velocity: Optional[float] = None      # month-on-month delta

    # ── Financial features ─────────────────────────────────────────────────
    expenditure_pct: Optional[float] = None        # cumulative_exp / current_cost * 100
    spending_progress_gap: Optional[float] = None  # expenditure_pct - physical_progress
    cost_escalation_pct: Optional[float] = None    # (revised-original)/original * 100
    expenditure_velocity: Optional[float] = None   # month-on-month delta (₹ Lakhs)

    # ── Schedule features ──────────────────────────────────────────────────
    schedule_escalation_days: Optional[int] = None  # revised_date - original_date
    is_past_original_deadline: bool = False

    # ── Milestone features ─────────────────────────────────────────────────
    total_milestones: int = 0
    completed_milestones: int = 0
    delayed_milestones: int = 0
    missed_milestones: int = 0
    milestone_completion_ratio: Optional[float] = None  # completed / total


def compute_features(
    *,
    physical_progress: Optional[float],
    planned_progress: Optional[float],
    cumulative_expenditure: Optional[float],
    current_cost: Optional[float],
    original_cost: Optional[float],
    original_start_date: Optional[date],
    original_completion_date: Optional[date],
    revised_completion_date: Optional[date],
    current_date: Optional[date] = None,
    prev_physical_progress: Optional[float] = None,
    prev_expenditure: Optional[float] = None,
    milestones: Optional[list] = None,
) -> ProjectFeatures:
    """
    Compute all derived features for a project snapshot.

    Parameters correspond to values from projects + project_snapshots tables.
    prev_* values come from the previous month's snapshot (may be None).
    milestones is a list of ORM Milestone objects (may be None or empty).
    """
    today = current_date or date.today()
    f = ProjectFeatures(
        physical_progress=physical_progress,
        planned_progress=planned_progress,
    )

    # ── Progress gap ─────────────────────────────────────────────────────
    if physical_progress is not None and planned_progress is not None:
        f.progress_gap = round(physical_progress - planned_progress, 2)

    # ── Progress velocity (month-on-month) ────────────────────────────────
    if physical_progress is not None and prev_physical_progress is not None:
        f.progress_velocity = round(physical_progress - prev_physical_progress, 2)

    # ── Time consumed ─────────────────────────────────────────────────────
    if original_start_date and original_completion_date:
        planned_duration = (original_completion_date - original_start_date).days
        if planned_duration > 0:
            elapsed = (today - original_start_date).days
            f.time_consumed_pct = round(min(elapsed / planned_duration * 100, 200), 2)
        days_remaining = (original_completion_date - today).days
        if days_remaining < 0:
            f.days_overdue = abs(days_remaining)
            f.is_past_original_deadline = True
        else:
            f.days_to_original_deadline = days_remaining

    # ── Expenditure % ─────────────────────────────────────────────────────
    cost_basis = current_cost or original_cost
    if cumulative_expenditure is not None and cost_basis and cost_basis > 0:
        f.expenditure_pct = round(cumulative_expenditure / cost_basis * 100, 2)

    # ── Spending-progress gap ─────────────────────────────────────────────
    if f.expenditure_pct is not None and physical_progress is not None:
        f.spending_progress_gap = round(f.expenditure_pct - physical_progress, 2)

    # ── Cost escalation ───────────────────────────────────────────────────
    if original_cost and original_cost > 0 and current_cost is not None:
        f.cost_escalation_pct = round(
            (current_cost - original_cost) / original_cost * 100, 2
        )

    # ── Schedule escalation ───────────────────────────────────────────────
    if original_completion_date and revised_completion_date:
        f.schedule_escalation_days = (revised_completion_date - original_completion_date).days

    # ── Expenditure velocity ──────────────────────────────────────────────
    if cumulative_expenditure is not None and prev_expenditure is not None:
        f.expenditure_velocity = round(cumulative_expenditure - prev_expenditure, 2)

    # ── Milestones ────────────────────────────────────────────────────────
    if milestones:
        f.total_milestones = len(milestones)
        f.completed_milestones = sum(1 for m in milestones if m.status == "completed")
        f.delayed_milestones = sum(1 for m in milestones if m.status == "delayed")
        f.missed_milestones = sum(1 for m in milestones if m.status == "missed")
        if f.total_milestones > 0:
            f.milestone_completion_ratio = round(
                f.completed_milestones / f.total_milestones, 3
            )

    return f
