"""
Ingestion — CSV Parser
Reads CSV files and extracts normalized project rows.
"""
from __future__ import annotations

import io
from datetime import date
from typing import Optional

import pandas as pd

from app.ingestion.mapper import map_row
from app.ingestion.normalizer import (
    normalize_cost, normalize_date, normalize_percentage,
    normalize_project_id, normalize_status, normalize_text,
)


def parse_csv(
    file_bytes: bytes,
    report_month: Optional[date] = None,
    encoding: str = "utf-8",
) -> list[dict]:
    """
    Parse a CSV file and return a list of normalized row dicts.
    Tries multiple encodings on failure.
    """
    for enc in [encoding, "utf-8-sig", "latin-1", "cp1252"]:
        try:
            df = pd.read_csv(io.BytesIO(file_bytes), encoding=enc, dtype=str, skip_blank_lines=True)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ValueError("Could not decode CSV file with any supported encoding")

    return _dataframe_to_rows(df, report_month)


def parse_excel(file_bytes: bytes, report_month: Optional[date] = None) -> list[dict]:
    """
    Parse an Excel file (.xlsx / .xls) and return normalized rows.
    Tries all sheets; returns rows from the first sheet that contains project data.
    """
    xl = pd.ExcelFile(io.BytesIO(file_bytes))
    for sheet in xl.sheet_names:
        df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=sheet, dtype=str)
        if df.empty:
            continue
        # Check if this sheet has project-like columns
        cols_lower = [str(c).lower() for c in df.columns]
        if any("project" in c or "id" in c or "progress" in c for c in cols_lower):
            return _dataframe_to_rows(df, report_month)
    # Fall back to first sheet
    df = pd.read_excel(io.BytesIO(file_bytes), sheet_name=0, dtype=str)
    return _dataframe_to_rows(df, report_month)


def _dataframe_to_rows(df: pd.DataFrame, report_month: Optional[date]) -> list[dict]:
    """Convert a DataFrame to normalized row dicts."""
    # Drop completely empty rows
    df = df.dropna(how="all")
    rows = []
    for _, raw_row in df.iterrows():
        raw = {str(k): (None if pd.isna(v) else str(v).strip()) for k, v in raw_row.items()}
        mapped = map_row(raw)
        normalized = _normalize_mapped_row(mapped, report_month)
        rows.append(normalized)
    return rows


def _normalize_mapped_row(mapped: dict, report_month: Optional[date]) -> dict:
    """Apply type normalizers to a canonically-mapped row."""
    return {
        "project_id": normalize_project_id(mapped.get("project_id")),
        "project_name": normalize_text(mapped.get("project_name")),
        "ministry": normalize_text(mapped.get("ministry")),
        "department": normalize_text(mapped.get("department")),
        "implementing_agency": normalize_text(mapped.get("implementing_agency")),
        "sector": normalize_text(mapped.get("sector")),
        "state": normalize_text(mapped.get("state")),
        "original_cost": normalize_cost(mapped.get("original_cost")),
        "revised_cost": normalize_cost(mapped.get("revised_cost")),
        "original_completion_date": normalize_date(mapped.get("original_completion_date")),
        "revised_completion_date": normalize_date(mapped.get("revised_completion_date")),
        "original_start_date": normalize_date(mapped.get("original_start_date")),
        "physical_progress": normalize_percentage(mapped.get("physical_progress")),
        "cumulative_expenditure": normalize_cost(mapped.get("cumulative_expenditure")),
        "current_status": normalize_status(mapped.get("current_status")),
        "report_month": report_month,
        "_unmapped": mapped.get("_unmapped", {}),
    }
