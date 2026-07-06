import uuid
from datetime import datetime

from pydantic import BaseModel, field_serializer


class AttachmentRead(BaseModel):
    id: uuid.UUID
    instrument_id: uuid.UUID
    filename: str
    original_filename: str
    file_size: int
    file_type: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id", "instrument_id")
    def serialize_uuid(self, value: uuid.UUID) -> str:
        return str(value)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()


class AttachmentInfo(BaseModel):
    id: uuid.UUID
    original_filename: str
    file_size: int
    file_type: str | None
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> str:
        return value.isoformat()
