from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest, TokenResponse, UserBrief


async def register_user(db: AsyncSession, data: RegisterRequest) -> TokenResponse:
    existing = await db.execute(
        select(User).where(User.username == data.username)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已被注册")

    user = User(
        username=data.username,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
        email=data.email or f"{data.username}@local",
    )
    db.add(user)
    await db.flush()

    return _generate_token_response(user)


async def authenticate_user(db: AsyncSession, username: str, password: str) -> TokenResponse:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被停用")

    return _generate_token_response(user)


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
    payload = decode_token(refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的刷新令牌")

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户不存在或已停用")

    return _generate_token_response(user)


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str) -> None:
    if not verify_password(old_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="原密码错误")
    user.hashed_password = hash_password(new_password)


async def change_username(db: AsyncSession, user: User, new_username: str) -> None:
    existing = await db.execute(select(User).where(User.username == new_username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已被使用")
    user.username = new_username


async def admin_set_password(db: AsyncSession, user_id: str, new_password: str) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    user.hashed_password = hash_password(new_password)


async def admin_set_username(db: AsyncSession, user_id: str, new_username: str) -> None:
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    existing = await db.execute(select(User).where(User.username == new_username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已被使用")
    user.username = new_username


def _generate_token_response(user: User) -> TokenResponse:
    token_data = {"sub": str(user.id)}
    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
        user=UserBrief(
            id=str(user.id),
            username=user.username,
            full_name=user.full_name,
            role=user.role,
        ),
    )
