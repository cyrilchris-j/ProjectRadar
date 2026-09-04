"""
Ingestion — Normalizer
Converts raw extracted string values into clean typed Python values.
Handles: Indian number formats, various date formats, percentage strings.
"""
from __future__ import annotations

import re
from datetime import date
from typing import Optional

from dateutil import parser as dateutil_parser


# ─── Cost / Number Normalization ─────────────────────────────────────────────

_LAKH = 1_00_000
_CRORE = 1_00_00_000

_COST_UNIT_MAP = {
    "crore": _CRORE / _LAKH,   # store everything in Lakhs
    "cr": _CRORE / _LAKH,
    "crores": _CRORE / _LAKH,
    "lakh": 1.0,
    "lacs": 1.0,
    "lac": 1.0,
    "lakhs": 1.0,
    "l": 1.0,
}


def normalize_cost(raw: Optional[str]) -> Optional[float]:
    """
    Convert a cost string to float in ₹ Lakhs.
    Examples: '₹1,234.56 Cr', '28500.00', '1,84,000 Lakhs', '18.5Cr'
    """
    if raw is None:
        return None
    text = str(raw).strip().lower()
    text = text.replace("₹", "").replace("rs.", "").replace("rs", "").replace(",", "").strip()

    # Detect unit suffix
    multiplier = 1.0
    for unit, factor in _COST_UNIT_MAP.items():
        if text.endswith(unit):
            text = text[: -len(unit)].strip()
            multiplier = factor
            break
        elif unit in text:
            # e.g. "18.5 cr" or "18.5crore"
            text = re.sub(rf"\b{unit}\b", "", text).strip()
            multiplier = factor
            break

    try:
        value = float(text)
        return round(value * multiplier, 2)
    except (ValueError, TypeError):
        return None


def normalize_percentage(raw: Optional[str]) -> Optional[float]:
    """
    Convert percentage string to float (0.0 – 100.0).
    Examples: '68%', '68.52', '0.685' (if < 1.0, multiply by 100)
    """
    if raw is None:
        return None
    text = str(raw).strip().replace("%", "").replace(",", "").strip()
    try:
        value = float(text)
        # If value looks like a decimal proportion (0.0–1.0), convert
        if 0.0 <= value <= 1.0 and "." in text:
            value = value * 100
        return round(min(max(value, 0.0), 100.0), 2)
    except (ValueError, TypeError):
        return None


def normalize_date(raw: Optional[str]) -> Optional[date]:
    """
    Parse various date strings to Python date.
    Examples: 'Mar-2027', '31/03/2027', '2027-03-31', 'March 2027'
    """
    if raw is None:
        return None
    text = str(raw).strip()
    if not text or text.lower() in ("na", "n/a", "-", "nil", ""):
        return None
    try:
        # Handle 'Mon-YYYY' format (e.g., 'Mar-2027')
        if re.match(r"^[A-Za-z]{3}-\d{4}$", text):
            return dateutil_parser.parse(text + "-01").date()
        return dateutil_parser.parse(text, dayfirst=True).date()
    except (ValueError, TypeError, OverflowError):
        return None


def normalize_project_id(raw: Optional[str]) -> Optional[str]:
    """Strip whitespace from project ID."""
    if raw is None:
        return None
    value = str(raw).strip()
    return value if value else None


def normalize_text(raw: Optional[str]) -> Optional[str]:
    """Clean text field: strip, collapse whitespace, None if empty."""
    if raw is None:
        return None
    value = re.sub(r"\s+", " ", str(raw)).strip()
    return value if value else None


def normalize_status(raw: Optional[str]) -> str:
    """Map raw status strings to canonical ProjectStatus enum values."""
    if raw is None:
        return "unknown"
    text = str(raw).strip().lower()
    _STATUS_MAP = {
        "ongoing": "ongoing",
        "in progress": "ongoing",
        "under implementation": "ongoing",
        "completed": "completed",
        "commissioned": "completed",
        "stalled": "stalled",
        "slow": "stalled",
        "delayed": "stalled",
        "abandoned": "abandoned",
        "dropped": "abandoned",
        "not started": "not_started",
        "yet to start": "not_started",
    }
    for key, value in _STATUS_MAP.items():
        if key in text:
            return value
    return "unknown"
