import json
from datetime import datetime, timezone, timedelta

import redis.asyncio as aioredis

from app.core.config import settings

redis_client: aioredis.Redis | None = None

BEIJING_TZ = timezone(timedelta(hours=8))

ONLINE_STATUS_TTL = 300


async def init_redis():
    global redis_client
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.aclose()
        redis_client = None


def get_redis() -> aioredis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis 未初始化")
    return redis_client


async def update_user_online_status(user_id: str, ip: str, user_agent: str):
    r = get_redis()
    key = f"online:{user_id}"
    value = json.dumps({
        "ip": ip,
        "ua": user_agent,
        "last_active": datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M:%S"),
    })
    await r.set(key, value, ex=ONLINE_STATUS_TTL)


async def get_user_online_status(user_id: str) -> dict | None:
    r = get_redis()
    key = f"online:{user_id}"
    raw = await r.get(key)
    if raw:
        return json.loads(raw)
    return None


async def get_all_users_online_status() -> dict[str, dict | None]:
    r = get_redis()
    pattern = "online:*"
    keys = []
    async for key in r.scan_iter(match=pattern):
        keys.append(key)

    result: dict[str, dict | None] = {}
    if keys:
        values = await r.mget(keys)
        for key, value in zip(keys, values):
            user_id = key.split(":", 1)[1]
            result[user_id] = json.loads(value) if value else None

    return result
