import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification
from app.schemas.notification import NotificationRead


async def create_notification(
    db: AsyncSession,
    user_id: uuid.UUID,
    type: str,
    title: str,
    message: str,
    related_booking_id: uuid.UUID | None = None,
) -> Notification:
    notif = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        related_booking_id=related_booking_id,
    )
    db.add(notif)
    await db.flush()
    return notif


async def get_user_notifications(
    db: AsyncSession, user_id: uuid.UUID, page: int = 1, per_page: int = 20
) -> tuple[list[Notification], int]:
    query = (
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc())
    )
    total = (
        await db.execute(
        select(func.count(Notification.id)).where(Notification.user_id == user_id)
        )
    ).scalar() or 0
    result = await db.execute(query.offset((page - 1) * per_page).limit(per_page))
    return list(result.scalars().all()), total


async def mark_read(db: AsyncSession, notification_id: uuid.UUID, user_id: uuid.UUID):
    notif = await db.get(Notification, notification_id)
    if notif is None or str(notif.user_id) != str(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="通知不存在")
    notif.is_read = True


async def mark_all_read(db: AsyncSession, user_id: uuid.UUID):
    result = await db.execute(
        select(Notification).where(Notification.user_id == user_id, Notification.is_read == False)
    )
    for n in result.scalars().all():
        n.is_read = True


async def get_unread_count(db: AsyncSession, user_id: uuid.UUID) -> int:
    return (
        await db.execute(
            select(func.count(Notification.id)).where(
                Notification.user_id == user_id, Notification.is_read == False
            )
        )
    ).scalar() or 0
