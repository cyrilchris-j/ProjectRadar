"""
Analytics — Forecasting Engine
Statistical forecasting for project completion and expenditure.
Uses linear regression and moving averages — no deep learning required.
Every forecast includes method metadata and uncertainty notes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Optional

import numpy as np


@dataclass
class ForecastResult:
    """
    Output of the forecasting engine.
    Always includes method used and a confidence/uncertainty note.
    """
    forecast_completion_date: Optional[date]
    forecast_progress_next_month: Optional[float]
    forecast_expenditure_next_month: Optional[float]
    expected_delay_days: Optional[int]
    method_used: str
    confidence_note: str


def forecast_project(
    snapshots: list[dict],
    original_completion_date: Optional[date],
    original_cost: Optional[float],
    current_date: Optional[date] = None,
) -> ForecastResult:
    """
    Forecast completion date and progress trajectory.

    snapshots: list of dicts with keys:
        report_month (date), physical_progress (float), cumulative_expenditure (float)
    Ordered chronologically (oldest first).
    """
    today = current_date or date.today()
    n = len(snapshots)

    if n < 2:
        return ForecastResult(
            forecast_completion_date=None,
            forecast_progress_next_month=None,
            forecast_expenditure_next_month=None,
            expected_delay_days=None,
            method_used="insufficient_data",
            confidence_note=(
                "Insufficient historical data for forecasting. "
                "At least 2 monthly observations are required."
            ),
        )

    # ── Extract time series ───────────────────────────────────────────────
    progress_series = [
        s["physical_progress"]
        for s in snapshots
        if s.get("physical_progress") is not None
    ]
    exp_series = [
        s["cumulative_expenditure"]
        for s in snapshots
        if s.get("cumulative_expenditure") is not None
    ]

    # ── Progress velocity (average monthly change) ────────────────────────
    if len(progress_series) >= 2:
        deltas = [progress_series[i] - progress_series[i-1] for i in range(1, len(progress_series))]
        avg_velocity = sum(deltas) / len(deltas)
    else:
        avg_velocity = None

    # ── Linear regression on progress ────────────────────────────────────
    method = "moving_average"
    if len(progress_series) >= 3:
        x = np.array(range(len(progress_series)), dtype=float)
        y = np.array(progress_series, dtype=float)
        slope, intercept = np.polyfit(x, y, 1)
        method = "linear_regression"
        next_progress = min(100.0, max(0.0, float(intercept + slope * len(progress_series))))
    elif avg_velocity is not None:
        next_progress = min(100.0, max(0.0, progress_series[-1] + avg_velocity))
    else:
        next_progress = None

    # ── Expenditure next month ────────────────────────────────────────────
    next_expenditure: Optional[float] = None
    if len(exp_series) >= 2:
        exp_deltas = [exp_series[i] - exp_series[i-1] for i in range(1, len(exp_series))]
        avg_exp_velocity = sum(exp_deltas) / len(exp_deltas)
        next_expenditure = round(exp_series[-1] + avg_exp_velocity, 2)

    # ── Forecast completion date ──────────────────────────────────────────
    forecast_date: Optional[date] = None
    delay_days: Optional[int] = None

    current_progress = progress_series[-1] if progress_series else None
    if current_progress is not None and avg_velocity is not None and avg_velocity > 0:
        remaining = 100.0 - current_progress
        months_needed = math.ceil(remaining / avg_velocity)
        last_month = snapshots[-1]["report_month"]
        forecast_date = _add_months(last_month, months_needed)

        if original_completion_date:
            delay_days = (forecast_date - original_completion_date).days
    elif original_completion_date and current_progress is not None and current_progress < 100:
        # Can't estimate — use original deadline with a warning
        forecast_date = None

    # ── Confidence note ───────────────────────────────────────────────────
    if n < 3:
        confidence = (
            f"Low confidence — based on only {n} monthly observation(s). "
            "Accuracy improves with more data points."
        )
    elif avg_velocity is not None and avg_velocity <= 0:
        confidence = (
            "Warning: Project progress velocity is zero or negative. "
            "Completion date cannot be reliably forecast."
        )
    else:
        confidence = (
            f"Moderate confidence — based on {n} monthly observations using {method.replace('_', ' ')}. "
            "Forecast assumes current pace continues."
        )

    return ForecastResult(
        forecast_completion_date=forecast_date,
        forecast_progress_next_month=round(next_progress, 2) if next_progress is not None else None,
        forecast_expenditure_next_month=next_expenditure,
        expected_delay_days=delay_days,
        method_used=method,
        confidence_note=confidence,
    )


def _add_months(d: date, months: int) -> date:
    """Add a number of months to a date."""
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                       31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
    return date(year, month, day)
