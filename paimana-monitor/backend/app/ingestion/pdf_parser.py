"""
Ingestion — PDF Parser
Extracts project data tables from PAIMANA Flash Report PDFs using pdfplumber.
Designed to be tolerant of:
  - Inconsistent spacing and column alignment
  - Wrapped cell text
  - Repeated headers across pages
  - Page breaks mid-table
  - Missing values
"""
from __future__ import annotations

import io
import re
from datetime import date
from typing import Optional

import pdfplumber
import pandas as pd

from app.ingestion.mapper import map_row
from app.ingestion.normalizer import (
    normalize_cost, normalize_date, normalize_percentage,
    normalize_project_id, normalize_status, normalize_text,
)


def parse_pdf(
    file_bytes: bytes,
    report_month: Optional[date] = None,
) -> list[dict]:
    """
    Extract project rows from a PAIMANA Flash Report PDF.
    Returns a list of normalized row dicts.
    """
    all_rows: list[dict] = []

    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        headers: list[str] = []
        for page_num, page in enumerate(pdf.pages, 1):
            tables = page.extract_tables({
                "vertical_strategy": "lines",
                "horizontal_strategy": "lines",
                "intersection_tolerance": 5,
                "snap_tolerance": 3,
            })

            if not tables:
                # Fall back to text-based extraction
                tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 2:
                    continue

                # Detect header row (first non-empty row)
                for i, row in enumerate(table):
                    cleaned = [_clean_cell(c) for c in row]
                    if _is_header_row(cleaned):
                        headers = cleaned
                        data_start = i + 1
                        break
                else:
                    # No header found in this table; use existing headers or skip
                    if not headers:
                        continue
                    data_start = 0

                # Extract data rows
                for row in table[data_start:]:
                    if not row:
                        continue
                    cleaned = [_clean_cell(c) for c in row]

                    # Skip rows that are repeated headers
                    if _is_header_row(cleaned):
                        continue

                    # Skip entirely blank rows
                    if all(not c for c in cleaned):
                        continue

                    if len(cleaned) < len(headers):
                        # Pad short rows
                        cleaned.extend([""] * (len(headers) - len(cleaned)))
                    elif len(cleaned) > len(headers):
                        cleaned = cleaned[:len(headers)]

                    raw_row = dict(zip(headers, cleaned))
                    mapped = map_row(raw_row)
                    normalized = _normalize_mapped_row(mapped, report_month)

                    # Only keep rows with at least a project_id
                    if normalized.get("project_id"):
                        all_rows.append(normalized)

    return all_rows


def _clean_cell(cell) -> str:
    """Clean a raw PDF cell value."""
    if cell is None:
        return ""
    # Collapse whitespace including newlines from wrapped cells
    return re.sub(r"\s+", " ", str(cell)).strip()


def _is_header_row(cells: list[str]) -> bool:
    """Heuristic: a row is a header if it contains typical header keywords."""
    combined = " ".join(cells).lower()
    header_keywords = [
        "project id", "project name", "project code",
        "progress", "expenditure", "ministry", "sector",
        "completion", "status", "sl no", "serial",
    ]
    matches = sum(1 for kw in header_keywords if kw in combined)
    return matches >= 2


def _normalize_mapped_row(mapped: dict, report_month: Optional[date]) -> dict:
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
