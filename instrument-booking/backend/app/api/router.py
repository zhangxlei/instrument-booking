from fastapi import APIRouter

from app.api.v1 import auth, instruments, bookings, admin, notifications, booking_reviews, lab_documents

router = APIRouter(prefix="/api/v1")
router.include_router(auth.router)
router.include_router(instruments.router)
router.include_router(bookings.router)
router.include_router(admin.router)
router.include_router(notifications.router)
router.include_router(booking_reviews.router)
router.include_router(lab_documents.router)
