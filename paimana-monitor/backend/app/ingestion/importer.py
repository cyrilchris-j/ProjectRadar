"""
Ingestion — Importer
Orchestrates the full pipeline: parsed rows → validation → database upsert → risk trigger.
Runs as a background task (non-blocking for web requests).
"""
from __future__ import annotations

import hashlib
import os
import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.orm import (
    Document, FileType, Import, ImportStatus,
    ProcessingStatus, Project, ProjectSnapshot,
)
from app.ingestion.normalizer import normalize_date
from app.ingestion.validator import validate_row
from app.risk.service import assess_all_projects_for_month
from app.config.settings import get_settings

settings = get_settings()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def detect_file_type(filename: str) -> FileType:
    ext = filename.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return FileType.pdf
    elif ext in ("xlsx", "xls", "xlsm"):
        return FileType.excel
    elif ext == "csv":
        return FileType.csv
    raise ValueError(f"Unsupported file type: .{ext}")


async def save_file(file_bytes: bytes, filename: str) -> str:
    """
    Save uploaded file to storage and return its storage path.
    Preserves original file; never modifies source.
    """
    base_path = settings.LOCAL_STORAGE_PATH
    today = datetime.utcnow()
    sub_path = os.path.join("reports", str(today.year), f"{today.month:02d}")
    full_dir = os.path.join(base_path, sub_path)
    os.makedirs(full_dir, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    full_path = os.path.join(full_dir, unique_name)
    with open(full_path, "wb") as f:
        f.write(file_bytes)
    return os.path.join(sub_path, unique_name)


async def create_document_record(
    db: AsyncSession,
    filename: str,
    file_bytes: bytes,
    storage_path: str,
    file_type: FileType,
    report_month: Optional[date],
    uploaded_by: Optional[uuid.UUID],
) -> Document:
    """Create the Document record and check for duplicates by hash."""
    file_hash = sha256_bytes(file_bytes)

    # Duplicate detection
    existing = await db.execute(
        select(Document).where(Document.file_hash == file_hash)
    )
    if existing.scalar_one_or_none():
        raise ValueError(f"This file has already been imported (hash: {file_hash[:8]}…)")

    doc = Document(
        filename=filename,
        file_type=file_type,
        storage_path=storage_path,
        file_size_bytes=len(file_bytes),
        file_hash=file_hash,
        report_month=report_month,
        processing_status=ProcessingStatus.queued,
        uploaded_by=uploaded_by,
    )
    db.add(doc)
    await db.flush()
    return doc


async def run_import(
    db: AsyncSession,
    import_record: Import,
    rows: list[dict],
    report_month: date,
) -> Import:
    """
    Execute the full import pipeline for a list of normalized rows.
    Updates the Import record with progress and results.
    """
    import_record.status = ImportStatus.processing
    import_record.started_at = datetime.utcnow()
    import_record.rows_found = len(rows)
    await db.flush()

    processed = 0
    rejected = 0
    duplicates = 0
    new_projects = 0
    updated_projects = 0
    rejected_details: list[dict] = []

    for row in rows:
        # Validate
        validation = validate_row(row, report_month)
        if not validation.is_valid:
            rejected += 1
            rejected_details.append({
                "project_id": row.get("project_id"),
                "project_name": row.get("project_name"),
                "errors": [
                    {"field": e.field, "value": e.value, "reason": e.reason}
                    for e in validation.errors
                ],
            })
            continue

        # Upsert Project
        project_id_str = row["project_id"]
        result = await db.execute(
            select(Project).where(Project.project_id == project_id_str)
        )
        project = result.scalar_one_or_none()

        if project is None:
            project = Project(
                project_id=project_id_str,
                project_name=row["project_name"],
                ministry=row.get("ministry"),
                department=row.get("department"),
                implementing_agency=row.get("implementing_agency"),
                sector=row.get("sector"),
                state=row.get("state"),
                original_cost=row.get("original_cost"),
                original_completion_date=row.get("original_completion_date"),
                original_start_date=row.get("original_start_date"),
                revised_cost=row.get("revised_cost"),
                revised_completion_date=row.get("revised_completion_date"),
            )
            db.add(project)
            await db.flush()
            new_projects += 1
        else:
            # Update mutable fields with latest values
            if row.get("project_name"):
                project.project_name = row["project_name"]
            if row.get("revised_cost") is not None:
                project.revised_cost = row["revised_cost"]
            if row.get("revised_completion_date"):
                project.revised_completion_date = row["revised_completion_date"]
            updated_projects += 1

        # Upsert ProjectSnapshot (one per project per month)
        snap_result = await db.execute(
            select(ProjectSnapshot).where(
                ProjectSnapshot.project_id == project.id,
                ProjectSnapshot.report_month == report_month,
            )
        )
        existing_snap = snap_result.scalar_one_or_none()

        if existing_snap:
            duplicates += 1
            # Update snapshot with new values (re-import overwrites)
            existing_snap.physical_progress = row.get("physical_progress")
            existing_snap.cumulative_expenditure = row.get("cumulative_expenditure")
            existing_snap.current_cost = row.get("revised_cost")
            existing_snap.current_completion_date = row.get("revised_completion_date")
            existing_snap.current_status = row.get("current_status", "unknown")
            existing_snap.source_document_id = import_record.document_id
        else:
            snap = ProjectSnapshot(
                project_id=project.id,
                report_month=report_month,
                physical_progress=row.get("physical_progress"),
                cumulative_expenditure=row.get("cumulative_expenditure"),
                current_cost=row.get("revised_cost"),
                current_completion_date=row.get("revised_completion_date"),
                current_status=row.get("current_status", "unknown"),
                raw_progress_value=str(row.get("physical_progress", "")),
                raw_expenditure_value=str(row.get("cumulative_expenditure", "")),
                raw_cost_value=str(row.get("revised_cost", "")),
                source_document_id=import_record.document_id,
            )
            db.add(snap)

        processed += 1

    await db.flush()

    # ── Trigger risk calculation for this report month ────────────────────
    risk_summary = await assess_all_projects_for_month(db, report_month)

    # ── Update import record ──────────────────────────────────────────────
    import_record.status = ImportStatus.completed if rejected == 0 else ImportStatus.partial
    import_record.rows_processed = processed
    import_record.rows_rejected = rejected
    import_record.duplicates = duplicates
    import_record.new_projects = new_projects
    import_record.updated_projects = updated_projects
    import_record.completed_at = datetime.utcnow()
    if rejected_details:
        import_record.error_details = {"rejected_rows": rejected_details}

    return import_record
