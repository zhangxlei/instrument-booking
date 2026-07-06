import os
import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.instrument import Instrument
from app.models.instrument_attachment import InstrumentAttachment
from app.schemas.instrument import InstrumentCreate, InstrumentUpdate

UPLOAD_DIR = "uploads/attachments"


async def create_instrument(db: AsyncSession, data: InstrumentCreate) -> Instrument:
    instrument = Instrument(**data.model_dump())
    db.add(instrument)
    await db.flush()
    return instrument


async def get_instrument(db: AsyncSession, instrument_id: uuid.UUID) -> Instrument:
    result = await db.execute(select(Instrument).where(Instrument.id == instrument_id))
    instrument = result.scalar_one_or_none()
    if instrument is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="仪器不存在")
    return instrument


async def get_instruments(
    db: AsyncSession,
    status_filter: str | None = None,
    search: str | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Instrument], int]:
    query = select(Instrument)

    if status_filter:
        query = query.where(Instrument.status == status_filter)
    if search:
        query = query.where(Instrument.name.ilike(f"%{search}%"))

    count_query = select(Instrument.id).select_from(Instrument)
    if status_filter:
        count_query = count_query.where(Instrument.status == status_filter)
    if search:
        count_query = count_query.where(Instrument.name.ilike(f"%{search}%"))

    total_result = await db.execute(count_query)
    total = len(total_result.all())

    query = query.order_by(Instrument.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)

    return list(result.scalars().all()), total


async def update_instrument(
    db: AsyncSession, instrument_id: uuid.UUID, data: InstrumentUpdate
) -> Instrument:
    instrument = await get_instrument(db, instrument_id)
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(instrument, key, value)
    return instrument


async def delete_instrument(db: AsyncSession, instrument_id: uuid.UUID):
    instrument = await get_instrument(db, instrument_id)
    await db.delete(instrument)


async def upload_attachment(
    db: AsyncSession,
    instrument_id: uuid.UUID,
    file: UploadFile,
    user_id: uuid.UUID,
) -> InstrumentAttachment:
    await get_instrument(db, instrument_id)

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    ext = ""
    if file.filename and "." in file.filename:
        ext = file.filename.rsplit(".", 1)[1].lower()
    stored_name = f"{uuid.uuid4()}.{ext}" if ext else str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, stored_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    attachment = InstrumentAttachment(
        instrument_id=instrument_id,
        filename=stored_name,
        original_filename=file.filename or stored_name,
        file_size=len(content),
        file_type=file.content_type,
        uploaded_by=user_id,
    )
    db.add(attachment)
    await db.flush()
    return attachment


async def get_attachments(db: AsyncSession, instrument_id: uuid.UUID) -> list[InstrumentAttachment]:
    result = await db.execute(
        select(InstrumentAttachment)
        .where(InstrumentAttachment.instrument_id == instrument_id)
        .order_by(InstrumentAttachment.created_at.desc())
    )
    return list(result.scalars().all())


async def get_attachment(
    db: AsyncSession, instrument_id: uuid.UUID, attachment_id: uuid.UUID
) -> InstrumentAttachment:
    result = await db.execute(
        select(InstrumentAttachment).where(
            InstrumentAttachment.id == attachment_id,
            InstrumentAttachment.instrument_id == instrument_id,
        )
    )
    attachment = result.scalar_one_or_none()
    if attachment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="附件不存在")
    return attachment


async def delete_attachment(db: AsyncSession, instrument_id: uuid.UUID, attachment_id: uuid.UUID):
    attachment = await get_attachment(db, instrument_id, attachment_id)
    file_path = os.path.join(UPLOAD_DIR, attachment.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    await db.delete(attachment)
