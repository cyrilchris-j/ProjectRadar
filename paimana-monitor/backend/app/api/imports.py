"""
Imports API — file upload, pipeline execution, status polling.
"""
import uuid
from datetime import date
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth import get_current_user, require_roles
from app.database.connection import get_db, get_db_context
from app.ingestion.csv_parser import parse_csv, parse_excel
from app.ingestion.importer import (
    create_document_record, detect_file_type, run_import, save_file,
)
from app.ingestion.normalizer import normalize_date
from app.ingestion.pdf_parser import parse_pdf
from app.models.orm import AuditLog, Document, FileType, Import, ImportStatus, User, UserRole
from app.schemas.schemas import DocumentOut, ImportOut

router = APIRouter(prefix="/api/imports", tags=["imports"])


async def _run_import_background(
    import_id: uuid.UUID,
    file_bytes: bytes,
    file_type: FileType,
    report_month: date,
):
    """Background task: parse file and run full import pipeline."""
    async with get_db_context() as db:
        result = await db.execute(select(Import).where(Import.id == import_id))
        import_record = result.scalar_one_or_none()
        if not import_record:
            return

        try:
            # Parse based on file type
            if file_type == FileType.pdf:
                rows = parse_pdf(file_bytes, report_month)
            elif file_type == FileType.excel:
                rows = parse_excel(file_bytes, report_month)
            else:
                rows = parse_csv(file_bytes, report_month)

            await run_import(db, import_record, rows, report_month)

        except Exception as e:
            import_record.status = ImportStatus.failed
            import_record.error_message = str(e)
            from datetime import datetime
            import_record.completed_at = datetime.utcnow()


@router.post("", response_model=ImportOut, status_code=202)
async def upload_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    report_month_str: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.analyst)),
):
    """
    Upload a PAIMANA report (PDF/Excel/CSV) and start background processing.
    Returns import_id for status polling.
    """
    # Read file
    file_bytes = await file.read()
    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Detect type
    try:
        file_type = detect_file_type(file.filename)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Parse report month
    report_month = normalize_date(report_month_str) if report_month_str else None
    if not report_month:
        # Default to start of current month
        from datetime import datetime
        today = datetime.utcnow().date()
        report_month = date(today.year, today.month, 1)

    # Save file to storage
    storage_path = await save_file(file_bytes, file.filename)

    # Create Document record (checks for duplicates)
    try:
        doc = await create_document_record(
            db=db,
            filename=file.filename,
            file_bytes=file_bytes,
            storage_path=storage_path,
            file_type=file_type,
            report_month=report_month,
            uploaded_by=current_user.id,
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    # Create Import record
    import_record = Import(
        document_id=doc.id,
        status=ImportStatus.pending,
        triggered_by=current_user.id,
    )
    db.add(import_record)
    await db.flush()

    # Audit log
    db.add(AuditLog(
        user_id=current_user.id,
        action="upload",
        entity_type="document",
        entity_id=str(doc.id),
        metadata={"filename": file.filename, "file_type": file_type.value, "report_month": str(report_month)},
    ))

    await db.commit()

    # Start background processing
    background_tasks.add_task(
        _run_import_background,
        import_record.id,
        file_bytes,
        file_type,
        report_month,
    )

    # Re-fetch to return
    result = await db.execute(select(Import).where(Import.id == import_record.id))
    return ImportOut.model_validate(result.scalar_one())


@router.get("/{import_id}", response_model=ImportOut)
async def get_import_status(
    import_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.analyst, UserRole.officer, UserRole.viewer)),
):
    result = await db.execute(select(Import).where(Import.id == import_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Import not found")
    return ImportOut.model_validate(record)


@router.get("", response_model=list[ImportOut])
async def list_imports(
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.admin, UserRole.analyst)),
):
    result = await db.execute(
        select(Import).order_by(desc(Import.created_at)).limit(limit)
    )
    return [ImportOut.model_validate(r) for r in result.scalars().all()]
