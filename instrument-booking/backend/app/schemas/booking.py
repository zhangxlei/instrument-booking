import uuid
from datetime import datetime

from pydantic import BaseModel, field_serializer


class BookingCreate(BaseModel):
    instrument_id: str
    start_time: datetime
    end_time: datetime
    purpose: str | None = None
    notes: str | None = None
    user_id: str | None = None


class BookingRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    instrument_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    status: str
    purpose: str | None
    notes: str | None
    rejection_reason: str | None
    created_at: datetime
    user_username: str | None = None
    user_full_name: str | None = None
    instrument_name: str | None = None

    model_config = {"from_attributes": True}

    @field_serializer("id", "user_id", "instrument_id")
    def serialize_uuid(self, value: uuid.UUID) -> str:
        return str(value)

    @field_serializer("start_time", "end_time", "created_at")
    def serialize_dt(self, value: datetime) -> str:
        return value.isoformat()


class BookingUpdate(BaseModel):
    start_time: datetime
    end_time: datetime


class BookingRejectRequest(BaseModel):
    reason: str
