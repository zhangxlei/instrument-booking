import uuid
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking import Booking
from app.models.instrument import Instrument, InstrumentMaintenance
from app.models.user import User
from app.schemas.booking import BookingCreate
from app.services.booking_review_service import create_review
from app.services.notification_service import create_notification


async def create_booking(
    db: AsyncSession, user_id: uuid.UUID, data: BookingCreate
) -> Booking:
    instrument = await db.get(Instrument, uuid.UUID(data.instrument_id))
    if instrument is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="仪器不存在")
    if instrument.status == "retired":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仪器已报废")
    if instrument.status == "maintenance":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仪器维护中")

    if data.end_time <= data.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="结束时间必须晚于开始时间")

    if data.start_time <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="预约时间不能早于当前时间")

    conflict = await _check_conflicts(db, instrument.id, data.start_time, data.end_time)
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该时段已被预约",
        )

    status_val = "pending" if instrument.requires_approval else "approved"

    booking = Booking(
        user_id=user_id,
        instrument_id=instrument.id,
        start_time=data.start_time,
        end_time=data.end_time,
        purpose=data.purpose,
        notes=data.notes,
        message=data.message,
        probe_type=data.probe_type,
        status=status_val,
    )
    db.add(booking)
    await db.flush()

    reviewer_id = uuid.UUID(data.reviewer_id) if data.reviewer_id else None
    await create_review(db, booking.id, reviewer_id)

    time_str = f"{data.start_time.strftime('%m/%d %H:%M')}"
    await create_notification(db, user_id, "booking_pending",
        "预约已提交", f"您的仪器预约（{time_str}）已提交，等待管理员审批", booking.id)

    admin_result = await db.execute(select(User).where(User.role == "admin"))
    for admin in admin_result.scalars().all():
        if str(admin.id) != str(user_id):
            await create_notification(db, admin.id, "booking_pending",
                "新预约待审批", f"用户提交了新的预约申请（{time_str}）", booking.id)

    return booking


async def cancel_booking(db: AsyncSession, booking_id: uuid.UUID, user_id: uuid.UUID):
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在")
    if str(booking.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能取消自己的预约")
    if booking.status not in ("pending", "approved"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能取消待审批或已批准的预约")
    booking.status = "cancelled"
    await create_notification(
        db, user_id, "booking_cancelled", "预约已取消",
        f"您的预约（{booking.start_time.strftime('%m/%d %H:%M')}）已取消",
        booking.id,
    )


async def list_user_bookings(
    db: AsyncSession,
    user_id: uuid.UUID,
    status_filter: str | None = None,
) -> list[Booking]:
    query = select(Booking).where(Booking.user_id == user_id)
    if status_filter:
        query = query.where(Booking.status == status_filter)
    query = query.order_by(Booking.created_at.desc())
    result = await db.execute(query)
    bookings = list(result.scalars().all())
    await _enrich_bookings(db, bookings)
    return bookings


async def get_booking(db: AsyncSession, booking_id: uuid.UUID) -> Booking | None:
    return await db.get(Booking, booking_id)


async def _check_conflicts(
    db: AsyncSession,
    instrument_id: uuid.UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_booking_id: uuid.UUID | None = None,
) -> bool:
    maint = await db.execute(
        select(InstrumentMaintenance).where(
            InstrumentMaintenance.instrument_id == instrument_id,
            InstrumentMaintenance.start_time < end_time,
            InstrumentMaintenance.end_time > start_time,
        )
    )
    if maint.scalar_one_or_none() is not None:
        return True
    query = select(Booking).where(
        Booking.instrument_id == instrument_id,
        Booking.status.in_(["pending", "approved"]),
        Booking.start_time < end_time,
        Booking.end_time > start_time,
    )
    if exclude_booking_id:
        query = query.where(Booking.id != exclude_booking_id)
    result = await db.execute(query)
    return result.scalar_one_or_none() is not None


async def approve_booking(db: AsyncSession, booking_id: uuid.UUID, admin_id: uuid.UUID) -> Booking:
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在")
    if booking.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能审批待审批的预约")

    conflict = await _check_conflicts(
        db, booking.instrument_id, booking.start_time, booking.end_time, booking_id
    )
    if conflict:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该时段已有其他被批准的预约")

    booking.status = "approved"
    booking.approved_by = admin_id
    booking.approved_at = datetime.now(timezone.utc)

    time_str = f"{booking.start_time.strftime('%m/%d %H:%M')}"
    await create_notification(db, booking.user_id, "booking_approved",
        "预约已批准", f"您的预约（{time_str}）已被批准", booking.id)

    return booking


async def reject_booking(
    db: AsyncSession, booking_id: uuid.UUID, admin_id: uuid.UUID, reason: str
) -> Booking:
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在")
    if booking.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能拒绝待审批的预约")

    booking.status = "rejected"
    booking.approved_by = admin_id
    booking.approved_at = datetime.now(timezone.utc)
    booking.rejection_reason = reason

    time_str = f"{booking.start_time.strftime('%m/%d %H:%M')}"
    await create_notification(db, booking.user_id, "booking_rejected",
        "预约已拒绝", f"您的预约（{time_str}）已被拒绝，原因：{reason}", booking.id)

    return booking


async def update_booking(
    db: AsyncSession, booking_id: uuid.UUID, user_id: uuid.UUID, start_time: datetime, end_time: datetime
) -> Booking:
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在")
    if str(booking.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="只能修改自己的预约")
    if booking.status not in ("pending", "approved"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="只能修改待审批或已批准的预约")
    if end_time <= start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="结束时间必须晚于开始时间")

    conflict = await _check_conflicts(db, booking.instrument_id, start_time, end_time, booking_id)
    if conflict:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该时段已被预约")

    booking.start_time = start_time
    booking.end_time = end_time
    if booking.status == "approved":
        booking.status = "pending"

    time_str = f"{start_time.strftime('%m/%d %H:%M')}"
    await create_notification(db, user_id, "booking_pending",
        "预约时间已修改", f"您的预约时间已修改为（{time_str}），等待管理员审批", booking.id)

    return booking


async def list_all_bookings(
    db: AsyncSession,
    status_filter: str | None = None,
    instrument_id: uuid.UUID | None = None,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[Booking], int]:
    query = select(Booking)
    if status_filter:
        query = query.where(Booking.status == status_filter)
    if instrument_id:
        query = query.where(Booking.instrument_id == instrument_id)
    query = query.order_by(Booking.created_at.desc())

    count_query = select(Booking.id).select_from(Booking)
    if status_filter:
        count_query = count_query.where(Booking.status == status_filter)
    total_result = await db.execute(count_query)
    total = len(total_result.all())

    query = query.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(query)
    bookings = list(result.scalars().all())
    await _enrich_bookings(db, bookings)
    return bookings, total


async def admin_reschedule_booking(
    db: AsyncSession, booking_id: uuid.UUID, start_time: datetime, end_time: datetime
) -> Booking:
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在")
    if end_time <= start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="结束时间必须晚于开始时间")
    booking.start_time = start_time
    booking.end_time = end_time
    return booking


async def admin_cancel_booking(db: AsyncSession, booking_id: uuid.UUID):
    booking = await db.get(Booking, booking_id)
    if booking is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="预约不存在")
    booking.status = "cancelled"


async def batch_cancel_bookings(db: AsyncSession, booking_ids: list[uuid.UUID]) -> int:
    result = await db.execute(
        select(Booking).where(Booking.id.in_(booking_ids))
    )
    bookings = result.scalars().all()
    count = 0
    for booking in bookings:
        if booking.status in ("pending", "approved"):
            booking.status = "cancelled"
            count += 1
    return count


async def admin_create_booking(db: AsyncSession, data) -> Booking:
    instrument = await db.get(Instrument, uuid.UUID(data.instrument_id))
    if instrument is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="仪器不存在")
    if instrument.status == "retired":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仪器已报废")
    if instrument.status == "maintenance":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="仪器维护中")
    if data.end_time <= data.start_time:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="结束时间必须晚于开始时间")
    if data.start_time <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="预约时间不能早于当前时间")

    conflict = await _check_conflicts(db, instrument.id, data.start_time, data.end_time)
    if conflict:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该时段已被预约",
        )

    user_id = uuid.UUID(data.user_id) if isinstance(data.user_id, str) else data.user_id
    status_val = "pending" if instrument.requires_approval else "approved"
    booking = Booking(
        user_id=user_id,
        instrument_id=instrument.id,
        start_time=data.start_time,
        end_time=data.end_time,
        purpose=data.purpose,
        notes=data.notes,
        message=data.message,
        probe_type=data.probe_type,
        status=status_val,
    )
    db.add(booking)
    await db.flush()

    reviewer_id = uuid.UUID(data.reviewer_id) if data.reviewer_id else None
    await create_review(db, booking.id, reviewer_id)

    time_str = f"{data.start_time.strftime('%m/%d %H:%M')}"
    await create_notification(db, user_id, "booking_pending",
        "管理员代预约", f"管理员为您预约了仪器（{time_str}），等待审批", booking.id)
    return booking


async def _enrich_bookings(db: AsyncSession, bookings: list[Booking]):
    if not bookings:
        return
    user_ids = {b.user_id for b in bookings}
    inst_ids = {b.instrument_id for b in bookings}
    users = await db.execute(select(User).where(User.id.in_(user_ids)))
    user_map = {u.id: u for u in users.scalars().all()}
    instruments = await db.execute(select(Instrument).where(Instrument.id.in_(inst_ids)))
    inst_map = {i.id: i for i in instruments.scalars().all()}
    for b in bookings:
        u = user_map.get(b.user_id)
        if u:
            b.user_username = u.username
            b.user_full_name = u.full_name
        i = inst_map.get(b.instrument_id)
        if i:
            b.instrument_name = i.name
