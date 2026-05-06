import logging
import os
import traceback
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            logger.error(
                "未处理异常: %s %s - %s\n%s",
                request.method,
                request.url.path,
                str(exc),
                traceback.format_exc(),
            )
            is_dev = os.environ.get("ENVIRONMENT") != "production"
            content = {"detail": "服务器内部错误"}
            if is_dev:
                content["error"] = str(exc)
                content["path"] = request.url.path
            return JSONResponse(
                status_code=500,
                content=content,
            )


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self._request_counts: dict[str, list[float]] = {}
        self._last_cleanup = time.time()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        from app.core.config import get_settings
        settings = get_settings()

        if not settings.ENABLE_RATE_LIMIT:
            return await call_next(request)

        if request.url.path.startswith(("/docs", "/redoc", "/openapi.json", "/metrics", "/health")):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window = 60.0

        if client_ip not in self._request_counts:
            self._request_counts[client_ip] = []

        self._request_counts[client_ip] = [
            t for t in self._request_counts[client_ip] if now - t < window
        ]

        if len(self._request_counts[client_ip]) >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={"detail": "请求过于频繁，请稍后再试"},
            )

        self._request_counts[client_ip].append(now)

        if now - self._last_cleanup > 300:
            self._cleanup_old_entries(now, window)
            self._last_cleanup = now

        return await call_next(request)

    def _cleanup_old_entries(self, now: float, window: float):
        expired_ips = [
            ip for ip, timestamps in self._request_counts.items()
            if not any(now - t < window for t in timestamps)
        ]
        for ip in expired_ips:
            del self._request_counts[ip]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        logger.info(
            "%s %s %d %.3fs",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response
