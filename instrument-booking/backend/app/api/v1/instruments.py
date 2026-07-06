import uuid
from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, require_admin
from app.models.user import User
from app.schemas.attachment import AttachmentInfo
from app.schemas.common import MessageResponse
from app.schemas.instrument import InstrumentCreate, InstrumentRead, InstrumentUpdate
from app.services import instrument_service
import os

router = APIRouter(prefix="/instruments", tags=["仪器"])


@router.get("", response_model=list[InstrumentRead])
async def list_instruments(
    status: str | None = None,
    search: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    items, _ = await instrument_service.get_instruments(db, status, search, page, per_page)
    return items


@router.get("/{instrument_id}/availability")
async def get_availability(
    instrument_id: uuid.UUID,
    days: int = Query(7, ge=1, le=3650),
    db: AsyncSession = Depends(get_db),
):
    from datetime import date, datetime, time, timedelta, timezone
    from sqlalchemy import select
    from app.models.booking import Booking
    from app.models.user import User
    from app.models.instrument import Instrument, InstrumentMaintenance

    inst = await db.get(Instrument, instrument_id)
    if inst is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="仪器不存在")

    today = date.today()
    result = []

    booking_result = await db.execute(
        select(Booking).where(
            Booking.instrument_id == instrument_id,
            Booking.status.in_(["pending", "approved"]),
            Booking.start_time >= datetime.combine(today, time.min, tzinfo=timezone.utc),
        ).order_by(Booking.start_time)
    )
    existing = booking_result.scalars().all()

    user_ids = {b.user_id for b in existing}
    user_map = {}
    if user_ids:
        users = await db.execute(select(User).where(User.id.in_(user_ids)))
        user_map = {u.id: u for u in users.scalars().all()}

    maint_result = await db.execute(
        select(InstrumentMaintenance).where(
            InstrumentMaintenance.instrument_id == instrument_id,
            InstrumentMaintenance.end_time >= datetime.combine(today, time.min, tzinfo=timezone.utc),
        )
    )
    maintenances = maint_result.scalars().all()

    for day_offset in range(days):
        day = today + timedelta(days=day_offset)
        day_start = datetime.combine(day, time(0, 0), tzinfo=timezone.utc)
        day_end = datetime.combine(day, time(23, 59), tzinfo=timezone.utc)

        slots = []
        current = day_start
        while current < day_end:
            slot_end = current + timedelta(hours=1)
            past = current < datetime.now(timezone.utc)

            booked_by = None
            for b in existing:
                if b.start_time < slot_end and b.end_time > current:
                    u = user_map.get(b.user_id)
                    booked_by = {"username": u.username, "full_name": u.full_name} if u else {"username": "未知", "full_name": "未知"}
                    break

            in_maint = any(
                m.start_time < slot_end and m.end_time > current
                for m in maintenances
            )

            available = not past and not booked_by and not in_maint

            slots.append({
                "start": current.strftime("%H:%M"),
                "end": slot_end.strftime("%H:%M"),
                "available": available,
                "booked_by": booked_by,
            })

            current = slot_end

        result.append({"date": day.isoformat(), "slots": slots})

    return result


@router.get("/{instrument_id}", response_model=InstrumentRead)
async def get_instrument(instrument_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await instrument_service.get_instrument(db, instrument_id)


@router.post("", response_model=InstrumentRead, status_code=201)
async def create_instrument(
    data: InstrumentCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await instrument_service.create_instrument(db, data)


@router.put("/{instrument_id}", response_model=InstrumentRead)
async def update_instrument(
    instrument_id: uuid.UUID,
    data: InstrumentUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    return await instrument_service.update_instrument(db, instrument_id, data)


@router.delete("/{instrument_id}", response_model=MessageResponse)
async def delete_instrument(
    instrument_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await instrument_service.delete_instrument(db, instrument_id)
    return MessageResponse(message="仪器已删除")


@router.post("/{instrument_id}/image", response_model=MessageResponse)
async def upload_instrument_image(
    instrument_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    inst = await instrument_service.get_instrument(db, instrument_id)
    os.makedirs("uploads/images", exist_ok=True)

    ext = ""
    if file.filename and "." in file.filename:
        ext = file.filename.rsplit(".", 1)[1].lower()
    stored_name = f"{instrument_id}.{ext}" if ext else str(instrument_id)
    file_path = os.path.join("uploads/images", stored_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    inst.image_url = f"/uploads/images/{stored_name}"
    return MessageResponse(message="图片上传成功")


@router.delete("/{instrument_id}/image", response_model=MessageResponse)
async def delete_instrument_image(
    instrument_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    inst = await instrument_service.get_instrument(db, instrument_id)
    if inst.image_url:
        file_name = inst.image_url.rsplit("/", 1)[-1]
        file_path = os.path.join("uploads/images", file_name)
        if os.path.exists(file_path):
            os.remove(file_path)
        inst.image_url = None
    return MessageResponse(message="图片已删除")


@router.post("/{instrument_id}/attachments", response_model=AttachmentInfo, status_code=201)
async def upload_attachment(
    instrument_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    return await instrument_service.upload_attachment(db, instrument_id, file, current_user.id)


@router.get("/{instrument_id}/attachments", response_model=list[AttachmentInfo])
async def list_attachments(instrument_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await instrument_service.get_attachments(db, instrument_id)


@router.get("/{instrument_id}/attachments/{attachment_id}")
async def download_attachment(
    instrument_id: uuid.UUID,
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    attachment = await instrument_service.get_attachment(db, instrument_id, attachment_id)
    file_path = os.path.join("uploads/attachments", attachment.filename)
    return FileResponse(
        file_path,
        filename=attachment.original_filename,
        media_type=attachment.file_type or "application/octet-stream",
    )


@router.delete("/{instrument_id}/attachments/{attachment_id}", response_model=MessageResponse)
async def delete_attachment(
    instrument_id: uuid.UUID,
    attachment_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await instrument_service.delete_attachment(db, instrument_id, attachment_id)
    return MessageResponse(message="附件已删除")
