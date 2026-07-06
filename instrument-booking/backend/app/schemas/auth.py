from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    email: str | None = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserBrief"


class UserBrief(BaseModel):
    id: str
    username: str
    full_name: str
    role: str

    model_config = {"from_attributes": True}


class RefreshRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str


class ChangeUsernameRequest(BaseModel):
    new_username: str


class AdminSetPasswordRequest(BaseModel):
    new_password: str


class AdminSetUsernameRequest(BaseModel):
    new_username: str
