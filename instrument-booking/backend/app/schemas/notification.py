import uuid
from datetime import datetime

from pydantic import BaseModel, field_serializer


class NotificationRead(BaseModel):
    id: uuid.UUID
    type: str
    title: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)

    @field_serializer("created_at")
    def serialize_dt(self, value: datetime) -> str:
        return value.isoformat()
