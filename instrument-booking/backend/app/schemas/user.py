import uuid
from pydantic import BaseModel, EmailStr, field_serializer


class UserCreate(BaseModel):
    username: str
    password: str
    full_name: str


class UserRead(BaseModel):
    id: uuid.UUID
    username: str
    full_name: str
    phone: str | None
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

    @field_serializer("id")
    def serialize_id(self, value: uuid.UUID) -> str:
        return str(value)


class UserUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None


class UserAdminUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None
