import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.booking_review import (
    AssignReviewerRequest,
    AssignTesterRequest,
    BookingReviewRead,
    ReviewCommentRequest,
)
from app.services import booking_review_service

router = APIRouter(prefix="/booking-reviews", tags=["审批流程"])


@router.get("/{booking_id}", response_model=BookingReviewRead | None)
async def get_review(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await booking_review_service.get_review_by_booking(db, booking_id)


@router.put("/{booking_id}/assign-reviewer", response_model=BookingReviewRead)
async def assign_reviewer(
    booking_id: uuid.UUID,
    data: AssignReviewerRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await booking_review_service.assign_reviewer(db, booking_id, uuid.UUID(data.reviewer_id))


@router.put("/{booking_id}/assign-tester", response_model=BookingReviewRead)
async def assign_tester(
    booking_id: uuid.UUID,
    data: AssignTesterRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await booking_review_service.assign_tester(db, booking_id, uuid.UUID(data.tester_id))


@router.put("/{booking_id}/approve", response_model=BookingReviewRead)
async def approve_review(
    booking_id: uuid.UUID,
    data: ReviewCommentRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await booking_review_service.approve_review(db, booking_id, data.comment)


@router.put("/{booking_id}/reject", response_model=BookingReviewRead)
async def reject_review(
    booking_id: uuid.UUID,
    data: ReviewCommentRequest,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await booking_review_service.reject_review(db, booking_id, data.comment)


@router.put("/{booking_id}/start-test", response_model=BookingReviewRead)
async def start_test(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await booking_review_service.start_test(db, booking_id)


@router.put("/{booking_id}/complete-test", response_model=BookingReviewRead)
async def complete_test(
    booking_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return await booking_review_service.complete_test(db, booking_id)
