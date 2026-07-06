import time

from fastapi import HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware

REQUEST_LIMIT = 5
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests: dict[str, list[float]] = {}

    async def dispatch(self, request: Request, call_next):
        if request.url.path.endswith("/auth/login"):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()
            timestamps = self.requests.get(client_ip, [])
            timestamps = [t for t in timestamps if now - t < WINDOW_SECONDS]
            if len(timestamps) >= REQUEST_LIMIT:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="登录尝试过于频繁，请稍后再试",
                )
            timestamps.append(now)
            self.requests[client_ip] = timestamps

        response = await call_next(request)
        return response
