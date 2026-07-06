import uuid
from datetime import datetime

from pydantic import BaseModel, field_serializer


class BookingReviewRead(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    reviewer_id: uuid.UUID | None = None
    tester_id: uuid.UUID | None = None
    status: str
    reviewer_comment: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id", "booking_id", "reviewer_id", "tester_id")
    def serialize_uuid(self, value: uuid.UUID | None) -> str | None:
        return str(value) if value else None

    @field_serializer("created_at", "updated_at")
    def serialize_dt(self, value: datetime) -> str:
        return value.isoformat()


class AssignReviewerRequest(BaseModel):
    reviewer_id: str


class AssignTesterRequest(BaseModel):
    tester_id: str


class ReviewCommentRequest(BaseModel):
    comment: str | None = None
