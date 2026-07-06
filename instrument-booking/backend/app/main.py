import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import router
from app.core.config import settings
from app.core.rate_limiter import RateLimitMiddleware


async def seed_super_admin():
    from app.core.database import async_session_factory
    from app.core.security import hash_password
    from app.models.user import User
    from sqlalchemy import select

    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.username == "oeinoadmin"))
        if not result.scalar_one_or_none():
            user = User(
                username="oeinoadmin",
                hashed_password=hash_password("oeinoadmin"),
                full_name="超级管理员",
                role="admin",
                email="oeinoadmin@local",
            )
            db.add(user)
            await db.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await seed_super_admin()
    yield


app = FastAPI(title="上海光电科技创新中心硅光实验室仪表预约系统", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware)
app.include_router(router)

os.makedirs("uploads/images", exist_ok=True)
app.mount("/uploads/images", StaticFiles(directory="uploads/images"), name="images")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
