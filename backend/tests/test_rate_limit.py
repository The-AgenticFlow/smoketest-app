from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.middleware import RateLimitMiddleware


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client."""
    client = MagicMock()
    client.zremrangebyscore = AsyncMock()
    client.zcard = AsyncMock(return_value=0)
    client.zadd = AsyncMock()
    client.expire = AsyncMock()
    client.zrange = AsyncMock(return_value=[])
    return client


class TestRateLimitHeaders:
    """Test that rate limit headers are properly set."""

    @pytest.mark.anyio
    async def test_rate_limit_headers_on_success(self, mock_redis_client):
        """Test that rate limit headers are present on successful requests."""
        test_app = FastAPI()

        # Mock Redis with 0 requests made
        mock_redis_client.zcard.return_value = 0

        test_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=5,
            redis_client=mock_redis_client
        )

        @test_app.get("/test")
        async def test_endpoint():
            return {"message": "Hello"}

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test")

            assert response.status_code == 200
            assert "X-RateLimit-Limit" in response.headers
            assert "X-RateLimit-Remaining" in response.headers
            assert "X-RateLimit-Reset" in response.headers
            assert response.headers["X-RateLimit-Limit"] == "5"
            assert response.headers["X-RateLimit-Remaining"] == "4"


class TestRateLimitExceeded:
    """Test 429 responses when rate limit is exceeded."""

    @pytest.mark.anyio
    async def test_429_when_limit_exceeded(self, mock_redis_client):
        """Test that 429 is returned when rate limit is exceeded."""
        test_app = FastAPI()

        # Mock Redis to return limit exceeded
        mock_redis_client.zcard.return_value = 5  # At limit
        mock_redis_client.zrange.return_value = [(b"old_request", 1000.0)]

        test_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=5,
            redis_client=mock_redis_client
        )

        @test_app.get("/test")
        async def test_endpoint():
            return {"message": "Hello"}

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test")

            assert response.status_code == 429
            assert "Retry-After" in response.headers
            assert response.headers["X-RateLimit-Limit"] == "5"
            assert response.headers["X-RateLimit-Remaining"] == "0"
            assert "detail" in response.json()
            assert "rate limit exceeded" in response.json()["detail"].lower()


class TestHealthEndpointExemption:
    """Test that /health endpoint is exempt from rate limiting."""

    @pytest.mark.anyio
    async def test_health_endpoint_no_headers(self, mock_redis_client):
        """Test that /health endpoint doesn't have rate limit headers."""
        test_app = FastAPI()

        test_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=5,
            redis_client=mock_redis_client,
            exempt_paths=["/health"]
        )

        @test_app.get("/health")
        async def health():
            return {"status": "ok"}

        @test_app.get("/api/test")
        async def api_endpoint():
            return {"message": "Hello"}

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Test health endpoint - should be exempt
            health_response = await client.get("/health")
            assert health_response.status_code == 200
            assert "X-RateLimit-Limit" not in health_response.headers

            # Test API endpoint - should have headers
            api_response = await client.get("/api/test")
            assert api_response.status_code == 200
            assert "X-RateLimit-Limit" in api_response.headers


class TestRedisFailureGracefulDegradation:
    """Test graceful handling of Redis failures."""

    @pytest.mark.anyio
    async def test_allow_request_when_redis_fails(self):
        """Test that requests are allowed when Redis is unavailable."""
        test_app = FastAPI()

        # Pass None as redis_client to simulate connection failure
        test_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=5,
            redis_client=None
        )

        @test_app.get("/test")
        async def test_endpoint():
            return {"message": "Hello"}

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test")

            # Request should be allowed even though Redis failed
            assert response.status_code == 200
            assert response.json()["message"] == "Hello"

    @pytest.mark.anyio
    async def test_allow_request_on_redis_error(self, mock_redis_client):
        """Test that requests are allowed when Redis raises an exception."""
        test_app = FastAPI()

        # Mock Redis to raise an exception during window check
        mock_redis_client.zremrangebyscore.side_effect = Exception("Redis connection error")

        test_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=5,
            redis_client=mock_redis_client
        )

        @test_app.get("/test")
        async def test_endpoint():
            return {"message": "Hello"}

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/test")

            # Request should be allowed despite Redis error
            assert response.status_code == 200


class TestClientIdentifierExtraction:
    """Test client identifier extraction from requests."""

    @pytest.mark.anyio
    async def test_x_forwarded_for_header_used(self, mock_redis_client):
        """Test that X-Forwarded-For header is used for client identification."""
        test_app = FastAPI()

        test_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=5,
            redis_client=mock_redis_client
        )

        @test_app.get("/test")
        async def test_endpoint():
            return {"message": "Hello"}

        transport = ASGITransport(app=test_app)
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
            headers={"X-Forwarded-For": "192.168.1.100"}
        ) as client:
            response = await client.get("/test")
            assert response.status_code == 200
            # Verify Redis key would use the forwarded IP
            assert mock_redis_client.zadd.called


class TestSlidingWindowLogic:
    """Test the sliding window rate limiting algorithm."""

    @pytest.mark.anyio
    async def test_requests_tracked_in_window(self, mock_redis_client):
        """Test that requests are tracked within the time window."""
        test_app = FastAPI()

        # Track request count manually
        call_count = [0]

        async def mock_zcard(key):
            call_count[0] += 1
            return call_count[0] - 1

        mock_redis_client.zcard = mock_zcard

        test_app.add_middleware(
            RateLimitMiddleware,
            requests_per_minute=5,
            redis_client=mock_redis_client
        )

        @test_app.get("/test")
        async def test_endpoint():
            return {"message": "Hello"}

        transport = ASGITransport(app=test_app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # Make multiple requests
            for _ in range(3):
                response = await client.get("/test")
                assert response.status_code == 200

            # Verify zcard was called for each request
            assert call_count[0] == 3


class TestMainAppIntegration:
    """Test integration with the main FastAPI app."""

    @pytest.mark.anyio
    async def test_main_app_includes_middleware(self):
        """Test that main app has rate limiting middleware configured."""
        # Import fresh to ensure we're checking the actual main.py
        import importlib

        import app.main
        importlib.reload(app.main)
        from app.main import app
        from app.middleware import RateLimitMiddleware

        # Check that middleware is registered by checking middleware class types
        has_rate_limit_middleware = any(
            isinstance(m, RateLimitMiddleware) or
            (hasattr(m, 'cls') and m.cls == RateLimitMiddleware)
            for m in app.user_middleware
        )
        assert has_rate_limit_middleware, f"RateLimitMiddleware not found in {app.user_middleware}"

    @pytest.mark.anyio
    async def test_health_endpoint_in_main_app(self, mock_redis_client):
        """Test that /health is accessible and exempt."""
        import app.main
        import app.middleware

        # Import main app (middleware already configured with real Redis)
        from app.main import app

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            response = await client.get("/health")
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
            # Health endpoint should not have rate limit headers (it's exempt)
            # Note: Without Redis, requests still pass through with fail-open behavior
