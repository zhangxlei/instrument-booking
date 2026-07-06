import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
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
