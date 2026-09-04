"""
Ingestion — Column Mapper
Maps source column names (as they appear in uploaded files) to canonical field names.
Configurable: add new aliases as real PAIMANA files are encountered.
"""
from __future__ import annotations

from typing import Optional


# ─── Canonical field → list of known aliases (case-insensitive) ────────────
FIELD_ALIASES: dict[str, list[str]] = {
    "project_id": [
        "project id", "project code", "projectid", "project_id",
        "proj id", "proj_id", "code", "serial no", "sl no",
        "project no", "proj no",
    ],
    "project_name": [
        "project name", "name of project", "project title",
        "description", "work description", "scheme name",
        "project_name",
    ],
    "ministry": [
        "ministry", "ministry/department", "nodal ministry",
        "administrative ministry",
    ],
    "department": [
        "department", "dept", "division",
    ],
    "implementing_agency": [
        "implementing agency", "agency", "executing agency",
        "implementation agency", "ia",
    ],
    "sector": [
        "sector", "category", "project category", "type",
    ],
    "state": [
        "state", "state/ut", "location state", "project state",
    ],
    "original_cost": [
        "original project cost", "original cost", "approved cost",
        "sanctioned cost", "project cost", "original_cost",
        "initial cost", "original contract value",
    ],
    "revised_cost": [
        "revised cost", "latest revised cost", "current cost",
        "revised project cost", "total revised cost", "revised_cost",
    ],
    "original_completion_date": [
        "original completion date", "scheduled completion",
        "original scheduled date", "planned completion",
        "original_completion_date", "date of completion (original)",
    ],
    "revised_completion_date": [
        "revised completion date", "latest completion date",
        "anticipated completion date", "revised_completion_date",
        "current completion date", "date of completion (revised)",
        "revised scheduled date",
    ],
    "original_start_date": [
        "original start date", "date of commencement",
        "commencement date", "start date",
    ],
    "physical_progress": [
        "physical progress", "progress", "% progress",
        "physical progress %", "completion percentage",
        "physical progress (%)","physical_progress",
        "progress %", "% complete", "percent complete",
    ],
    "cumulative_expenditure": [
        "cumulative expenditure", "expenditure", "cumulative exp",
        "total expenditure", "amount spent", "exp. incurred",
        "cumulative_expenditure", "actual expenditure",
        "expenditure incurred",
    ],
    "current_status": [
        "status", "project status", "current status",
        "implementation status",
    ],
}


def _normalize_key(key: str) -> str:
    """Lowercase, strip, collapse whitespace for comparison."""
    import re
    return re.sub(r"\s+", " ", key.strip().lower())


# Build reverse lookup: normalized_alias → canonical_field
_ALIAS_TO_FIELD: dict[str, str] = {}
for canonical, aliases in FIELD_ALIASES.items():
    for alias in aliases:
        _ALIAS_TO_FIELD[_normalize_key(alias)] = canonical
    _ALIAS_TO_FIELD[_normalize_key(canonical)] = canonical


def map_column(raw_column_name: str) -> Optional[str]:
    """
    Map a raw column name from an uploaded file to its canonical field name.
    Returns None if no mapping found.
    """
    return _ALIAS_TO_FIELD.get(_normalize_key(raw_column_name))


def map_row(raw_row: dict) -> dict:
    """
    Map all keys in a raw row dict to canonical field names.
    Unmapped columns are stored under '_unmapped'.
    """
    mapped: dict = {}
    unmapped: dict = {}
    for key, value in raw_row.items():
        canonical = map_column(str(key))
        if canonical:
            mapped[canonical] = value
        else:
            unmapped[str(key)] = value
    mapped["_unmapped"] = unmapped
    return mapped
