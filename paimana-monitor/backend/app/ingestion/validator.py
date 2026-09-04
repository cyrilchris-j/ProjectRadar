"""
Ingestion — Row Validator
Validates normalized row data before database insertion.
Returns structured validation errors — never silently accepts bad data.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class ValidationError:
    field: str
    value: str
    reason: str


@dataclass
class ValidationResult:
    is_valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, field_name: str, value, reason: str):
        self.is_valid = False
        self.errors.append(ValidationError(field=field_name, value=str(value), reason=reason))

    def add_warning(self, message: str):
        self.warnings.append(message)


def validate_row(row: dict, report_month: Optional[date] = None) -> ValidationResult:
    """
    Validate a normalized (canonical field names) row before insertion.
    """
    result = ValidationResult(is_valid=True)

    # ── Required fields ────────────────────────────────────────────────────
    if not row.get("project_id"):
        result.add_error("project_id", row.get("project_id"), "Project ID is required")

    if not row.get("project_name"):
        result.add_error("project_name", row.get("project_name"), "Project name is required")

    # ── Physical progress ──────────────────────────────────────────────────
    progress = row.get("physical_progress")
    if progress is not None:
        if not isinstance(progress, (int, float)):
            result.add_error("physical_progress", progress, "Must be a number")
        elif not (0 <= progress <= 100):
            result.add_error("physical_progress", progress, f"Must be 0–100, got {progress}")

    # ── Costs ─────────────────────────────────────────────────────────────
    for cost_field in ("original_cost", "revised_cost", "cumulative_expenditure"):
        cost = row.get(cost_field)
        if cost is not None:
            if not isinstance(cost, (int, float)):
                result.add_error(cost_field, cost, "Must be numeric")
            elif cost < 0:
                result.add_error(cost_field, cost, "Cost cannot be negative")

    # ── Date logic ────────────────────────────────────────────────────────
    orig_date = row.get("original_completion_date")
    rev_date = row.get("revised_completion_date")
    start_date = row.get("original_start_date")

    if orig_date and not isinstance(orig_date, date):
        result.add_error("original_completion_date", orig_date, "Invalid date format")

    if rev_date and not isinstance(rev_date, date):
        result.add_error("revised_completion_date", rev_date, "Invalid date format")

    if start_date and orig_date and isinstance(start_date, date) and isinstance(orig_date, date):
        if start_date >= orig_date:
            result.add_warning(f"Start date ({start_date}) is on or after completion date ({orig_date})")

    # ── Expenditure vs cost sanity ────────────────────────────────────────
    exp = row.get("cumulative_expenditure")
    cost = row.get("revised_cost") or row.get("original_cost")
    if exp is not None and cost is not None and isinstance(exp, float) and isinstance(cost, float):
        if exp > cost * 1.5:
            result.add_warning(
                f"Expenditure ({exp:,.2f}) exceeds 150% of project cost ({cost:,.2f}) — verify values"
            )

    return result
