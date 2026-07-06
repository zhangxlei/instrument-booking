import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.booking_review import BookingReview


async def get_review_by_booking(db: AsyncSession, booking_id: uuid.UUID) -> BookingReview | None:
    result = await db.execute(
        select(BookingReview).where(BookingReview.booking_id == booking_id)
    )
    return result.scalar_one_or_none()


async def create_review(db: AsyncSession, booking_id: uuid.UUID) -> BookingReview:
    review = BookingReview(booking_id=booking_id, status="pending_review")
    db.add(review)
    await db.flush()
    return review


async def assign_reviewer(db: AsyncSession, booking_id: uuid.UUID, reviewer_id: uuid.UUID) -> BookingReview:
    review = await get_review_by_booking(db, booking_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批记录不存在")
    review.reviewer_id = reviewer_id
    review.status = "pending_review"
    return review


async def assign_tester(db: AsyncSession, booking_id: uuid.UUID, tester_id: uuid.UUID) -> BookingReview:
    review = await get_review_by_booking(db, booking_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批记录不存在")
    review.tester_id = tester_id
    return review


async def approve_review(db: AsyncSession, booking_id: uuid.UUID, comment: str | None = None) -> BookingReview:
    review = await get_review_by_booking(db, booking_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批记录不存在")
    review.status = "review_approved"
    if comment:
        review.reviewer_comment = comment
    return review


async def reject_review(db: AsyncSession, booking_id: uuid.UUID, comment: str | None = None) -> BookingReview:
    review = await get_review_by_booking(db, booking_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批记录不存在")
    review.status = "review_rejected"
    if comment:
        review.reviewer_comment = comment
    return review


async def start_test(db: AsyncSession, booking_id: uuid.UUID) -> BookingReview:
    review = await get_review_by_booking(db, booking_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批记录不存在")
    review.status = "testing"
    return review


async def complete_test(db: AsyncSession, booking_id: uuid.UUID) -> BookingReview:
    review = await get_review_by_booking(db, booking_id)
    if review is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="审批记录不存在")
    review.status = "completed"
    return review
