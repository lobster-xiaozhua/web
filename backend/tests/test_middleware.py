import pytest
import time
from unittest.mock import MagicMock
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.middleware import ErrorHandlerMiddleware, RateLimitMiddleware, RequestLoggingMiddleware


class TestErrorHandlerMiddleware:
    @pytest.mark.asyncio
    async def test_dispatch_passes_through_success(self):
        app = MagicMock()
        middleware = ErrorHandlerMiddleware(app)

        async def mock_call_next(request):
            return Response(content="OK")

        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/test"
        request.client = MagicMock(host="127.0.0.1")

        response = await middleware.dispatch(request, mock_call_next)
        assert response.body == b"OK"

    @pytest.mark.asyncio
    async def test_dispatch_catches_exception(self):
        app = MagicMock()
        middleware = ErrorHandlerMiddleware(app)

        async def mock_call_next(request):
            raise ValueError("Test error")

        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/test"
        request.client = MagicMock(host="127.0.0.1")

        response = await middleware.dispatch(request, mock_call_next)
        assert isinstance(response, JSONResponse)
        assert response.status_code == 500
        data = response.body.decode()
        assert "服务器内部错误" in data or "error" in data.lower()


class TestRateLimitMiddleware:
    def test_rate_limit_initialization(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=100)
        assert middleware.requests_per_minute == 100

    @pytest.mark.asyncio
    async def test_rate_limit_bypasses_health_endpoints(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)

        async def mock_call_next(request):
            return Response(content="OK")

        request = MagicMock(spec=Request)
        request.url.path = "/health"

        response = await middleware.dispatch(request, mock_call_next)
        assert response.body == b"OK"

    @pytest.mark.asyncio
    async def test_rate_limit_bypasses_docs_endpoints(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)

        async def mock_call_next(request):
            return Response(content="OK")

        request = MagicMock(spec=Request)
        request.url.path = "/docs"

        response = await middleware.dispatch(request, mock_call_next)
        assert response.body == b"OK"

    @pytest.mark.asyncio
    async def test_rate_limit_allows_requests_under_limit(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)

        async def mock_call_next(request):
            return Response(content="OK")

        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.client = MagicMock(host="192.168.1.1")

        response = await middleware.dispatch(request, mock_call_next)
        assert response.body == b"OK"

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_excessive_requests(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=3)

        async def mock_call_next(request):
            return Response(content="OK")

        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.client = MagicMock(host="192.168.1.100")

        middleware._request_counts["192.168.1.100"] = [time.time() - 10] * 3

        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 429
        data = response.body.decode()
        assert "过于频繁" in data or "rate" in data.lower()

    @pytest.mark.asyncio
    async def test_rate_limit_window_cleanup(self):
        app = MagicMock()
        middleware = RateLimitMiddleware(app, requests_per_minute=60)

        async def mock_call_next(request):
            return Response(content="OK")

        request = MagicMock(spec=Request)
        request.url.path = "/api/test"
        request.client = MagicMock(host="10.0.0.1")

        middleware._request_counts["10.0.0.1"] = [time.time() - 120]

        response = await middleware.dispatch(request, mock_call_next)
        assert response.status_code == 200
        assert len(middleware._request_counts["10.0.0.1"]) == 1


class TestRequestLoggingMiddleware:
    @pytest.mark.asyncio
    async def test_logs_request_duration(self, caplog):
        import logging
        app = MagicMock()
        middleware = RequestLoggingMiddleware(app)

        async def mock_call_next(request):
            return Response(content="OK")

        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url.path = "/api/test"
        request.client = MagicMock(host="127.0.0.1")

        with caplog.at_level(logging.INFO):
            response = await middleware.dispatch(request, mock_call_next)

        assert response.status_code == 200
        assert len(caplog.records) >= 1
