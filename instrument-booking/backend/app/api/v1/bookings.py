import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.attachment import AttachmentInfo
from app.schemas.booking import BookingCreate, BookingRead, BookingUpdate
from app.schemas.common import MessageResponse
from app.services import booking_service

router = APIRouter(prefix="/bookings", tags=["预约"])


@router.get("", response_model=list[BookingRead])
async def list_bookings(
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.list_user_bookings(db, current_user.id, status)


@router.get("/{booking_id}", response_model=BookingRead)
async def get_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = await booking_service.get_booking(db, booking_id)
    if booking is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="预约不存在")
    if str(booking.user_id) != str(current_user.id):
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="无权查看他人预约")
    return booking


@router.post("", response_model=BookingRead, status_code=201)
async def create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.create_booking(db, current_user.id, data)


@router.put("/{booking_id}", response_model=BookingRead)
async def update_booking(
    booking_id: uuid.UUID,
    data: BookingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await booking_service.update_booking(db, booking_id, current_user.id, data.start_time, data.end_time)


@router.delete("/{booking_id}", response_model=MessageResponse)
async def cancel_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await booking_service.cancel_booking(db, booking_id, current_user.id)
    return MessageResponse(message="预约已取消")


import os
from fastapi import UploadFile, HTTPException, status
from fastapi.responses import FileResponse
from app.models.booking_document import BookingDocument


@router.post("/{booking_id}/documents", response_model=AttachmentInfo, status_code=201)
async def upload_booking_document(
    booking_id: uuid.UUID,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    os.makedirs("uploads/booking_docs", exist_ok=True)
    import uuid as uuid_lib
    ext = file.filename.rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    stored_name = f"{uuid_lib.uuid4()}.{ext}" if ext else str(uuid_lib.uuid4())
    file_path = os.path.join("uploads/booking_docs", stored_name)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    doc = BookingDocument(
        booking_id=booking_id,
        filename=stored_name,
        original_filename=file.filename or stored_name,
        file_size=len(content),
        file_type=file.content_type,
        uploaded_by=current_user.id,
    )
    db.add(doc)
    await db.flush()
    return doc


@router.get("/{booking_id}/documents", response_model=list[AttachmentInfo])
async def list_booking_documents(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.booking_document import BookingDocument
    result = await db.execute(
        select(BookingDocument).where(BookingDocument.booking_id == booking_id).order_by(BookingDocument.created_at.desc())
    )
    return result.scalars().all()


@router.get("/{booking_id}/documents/{doc_id}")
async def download_booking_document(
    booking_id: uuid.UUID,
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    from sqlalchemy import select
    from app.models.booking_document import BookingDocument
    result = await db.execute(
        select(BookingDocument).where(BookingDocument.id == doc_id, BookingDocument.booking_id == booking_id)
    )
    doc = result.scalar_one_or_none()
    if doc is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文档不存在")
    file_path = os.path.join("uploads/booking_docs", doc.filename)
    return FileResponse(
        file_path,
        filename=doc.original_filename,
        media_type=doc.file_type or "application/octet-stream",
    )
