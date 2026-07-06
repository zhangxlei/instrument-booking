import uuid
from datetime import datetime

from pydantic import BaseModel, field_serializer


class LabDocumentCreate(BaseModel):
    title: str
    content: str | None = None
    file_url: str | None = None
    is_published: bool = True
    is_login_notice: bool = False


class LabDocumentRead(BaseModel):
    id: uuid.UUID
    title: str
    content: str | None
    file_url: str | None
    is_published: bool
    is_login_notice: bool
    created_at: datetime

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)

    @field_serializer("created_at")
    def serialize_dt(self, value: datetime) -> str:
        return value.isoformat()
