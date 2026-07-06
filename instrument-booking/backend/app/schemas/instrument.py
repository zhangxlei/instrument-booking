import uuid

from pydantic import BaseModel, field_serializer


class InstrumentCreate(BaseModel):
    name: str
    description: str | None = None
    location: str | None = None
    image_url: str | None = None
    requires_approval: bool = True
    price_per_hour: float | None = None
    manager_name: str | None = None
    manager_phone: str | None = None
    probe_type: str | None = None


class InstrumentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    location: str | None = None
    image_url: str | None = None
    status: str | None = None
    requires_approval: bool | None = None
    price_per_hour: float | None = None
    manager_name: str | None = None
    manager_phone: str | None = None
    probe_type: str | None = None


class InstrumentRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None
    location: str | None
    image_url: str | None
    status: str
    requires_approval: bool
    price_per_hour: float | None
    manager_name: str | None
    manager_phone: str | None
    probe_type: str | None

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)
