import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, select


class BatchCancelRequest(BaseModel):
    booking_ids: list[str]
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_admin
from app.core.security import hash_password
from app.models.booking import Booking
from app.models.instrument import Instrument, InstrumentMaintenance
from app.models.user import User
from app.schemas.auth import AdminSetPasswordRequest, AdminSetUsernameRequest
from app.schemas.booking import BookingCreate, BookingRead, BookingRejectRequest, BookingUpdate
from app.schemas.common import MessageResponse
from app.schemas.user import UserRead
from app.services import auth_service, booking_service, export_service

router = APIRouter(prefix="/admin", tags=["管理后台"])


@router.get("/bookings", response_model=list[BookingRead])
async def list_all_bookings(
    status: str | None = None,
    instrument_id: str | None = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    inst_id = uuid.UUID(instrument_id) if instrument_id else None
    items, _ = await booking_service.list_all_bookings(db, status, inst_id, page, per_page)
    return items


@router.put("/bookings/{booking_id}/approve", response_model=BookingRead)
async def approve_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await booking_service.approve_booking(db, booking_id, admin.id)


@router.put("/bookings/{booking_id}/reject", response_model=BookingRead)
async def reject_booking(
    booking_id: uuid.UUID,
    data: BookingRejectRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await booking_service.reject_booking(db, booking_id, admin.id, data.reason)


@router.get("/dashboard/stats")
async def dashboard_stats(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    inst_count = (await db.execute(select(func.count(Instrument.id)))).scalar() or 0
    user_count = (await db.execute(select(func.count(User.id)))).scalar() or 0

    today_bookings = (
        await db.execute(
            select(func.count(Booking.id)).where(
                Booking.created_at >= func.current_date()
            )
        )
    ).scalar() or 0

    pending = (
        await db.execute(
            select(func.count(Booking.id)).where(Booking.status == "pending")
        )
    ).scalar() or 0

    return {
        "total_instruments": inst_count,
        "total_users": user_count,
        "today_bookings": today_bookings,
        "pending_approvals": pending,
    }


class MaintenanceCreate(BaseModel):
    instrument_id: str
    start_time: datetime
    end_time: datetime
    reason: str | None = None


class MaintenanceRead(MaintenanceCreate):
    id: str

    model_config = {"from_attributes": True}


@router.post("/maintenance", response_model=MaintenanceRead, status_code=201)
async def create_maintenance(
    data: MaintenanceCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    mt = InstrumentMaintenance(
        instrument_id=data.instrument_id,
        start_time=data.start_time,
        end_time=data.end_time,
        reason=data.reason,
    )
    db.add(mt)
    await db.flush()
    return mt


@router.get("/maintenance", response_model=list[MaintenanceRead])
async def list_maintenance(
    instrument_id: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    query = select(InstrumentMaintenance).order_by(InstrumentMaintenance.start_time.desc())
    if instrument_id:
        query = query.where(InstrumentMaintenance.instrument_id == instrument_id)
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/export/bookings")
async def export_bookings(
    start_date: str | None = None,
    end_date: str | None = None,
    instrument_id: str | None = None,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    from fastapi.responses import StreamingResponse
    import io

    wb = await export_service.export_bookings_excel(db, start_date, end_date, instrument_id, status)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=bookings.xlsx"},
    )


@router.get("/export/instruments")
async def export_instruments(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    from fastapi.responses import StreamingResponse
    import io

    wb = await export_service.export_instruments_excel(db)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=instruments.xlsx"},
    )


# ── 用户管理 ──

class UserAdminCreate(BaseModel):
    username: str
    full_name: str
    password: str
    role: str = "user"


class UserRoleUpdate(BaseModel):
    role: str


@router.get("/users", response_model=list[UserRead])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return result.scalars().all()


@router.post("/users", response_model=UserRead, status_code=201)
async def admin_create_user(
    data: UserAdminCreate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    existing = await db.execute(select(User).where(User.username == data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已被注册")
    user = User(
        username=data.username,
        full_name=data.full_name,
        hashed_password=hash_password(data.password),
        role=data.role,
        email=f"{data.username}@local",
    )
    db.add(user)
    await db.flush()
    return user


@router.put("/users/{user_id}/role", response_model=MessageResponse)
async def admin_change_user_role(
    user_id: uuid.UUID,
    data: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    if data.role not in ("admin", "user"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效角色")
    user.role = data.role
    return MessageResponse(message="角色已更新")


@router.put("/users/{user_id}/toggle-active", response_model=MessageResponse)
async def admin_toggle_user_active(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    user.is_active = not user.is_active
    return MessageResponse(message=f"用户已{'启用' if user.is_active else '禁用'}")


@router.put("/users/{user_id}/password", response_model=MessageResponse)
async def admin_set_user_password(
    user_id: uuid.UUID,
    data: AdminSetPasswordRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await auth_service.admin_set_password(db, str(user_id), data.new_password)
    return MessageResponse(message="密码已重置")


@router.put("/users/{user_id}/username", response_model=MessageResponse)
async def admin_set_user_username(
    user_id: uuid.UUID,
    data: AdminSetUsernameRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await auth_service.admin_set_username(db, str(user_id), data.new_username)
    return MessageResponse(message="用户名已修改")


@router.delete("/users/{user_id}", response_model=MessageResponse)
async def admin_delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin_user: User = Depends(require_admin),
):
    if str(user_id) == str(admin_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能删除自己")
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    await db.delete(user)
    return MessageResponse(message="用户已删除")


# ── 管理员预约管理 ──

@router.put("/bookings/{booking_id}/reschedule", response_model=BookingRead)
async def admin_reschedule_booking(
    booking_id: uuid.UUID,
    data: BookingUpdate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await booking_service.admin_reschedule_booking(db, booking_id, data.start_time, data.end_time)


@router.delete("/bookings/{booking_id}", response_model=MessageResponse)
async def admin_cancel_booking(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    await booking_service.admin_cancel_booking(db, booking_id)
    return MessageResponse(message="预约已取消")


@router.post("/bookings/batch-cancel", response_model=MessageResponse)
async def admin_batch_cancel(
    data: BatchCancelRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    ids = [uuid.UUID(bid) for bid in data.booking_ids]
    count = await booking_service.batch_cancel_bookings(db, ids)
    return MessageResponse(message=f"已取消 {count} 条预约")


@router.post("/bookings", response_model=BookingRead, status_code=201)
async def admin_create_booking(
    data: BookingCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(require_admin),
):
    return await booking_service.admin_create_booking(db, data)


@router.delete("/maintenance/{maintenance_id}", response_model=MessageResponse)
async def delete_maintenance(
    maintenance_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(require_admin),
):
    mt = await db.get(InstrumentMaintenance, maintenance_id)
    if mt is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="维护记录不存在")
    await db.delete(mt)
    return MessageResponse(message="维护记录已删除")
