import logging
import time

import redis.asyncio as redis
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Redis-backed rate limiting middleware using sliding window algorithm.

    Tracks requests per client IP address and limits to N requests per minute.
    Returns 429 status when limit exceeded with Retry-After header.
    Exempts /health endpoint from rate limiting.
    """

    def __init__(
        self,
        app: ASGIApp,
        redis_url: str = None,
        requests_per_minute: int = None,
        exempt_paths: list = None,
        redis_client: redis.Redis = None
    ):
        super().__init__(app)
        self.redis_url = redis_url or settings.redis_url
        self.requests_per_minute = requests_per_minute or getattr(
            settings, 'rate_limit_per_minute', 100
        )
        self.exempt_paths = exempt_paths or ['/health']
        self._redis_client: redis.Redis | None = redis_client
        self._window_size = 60  # 60 seconds window
        self._init_complete = False

    async def _get_redis_client(self) -> redis.Redis | None:
        """Get or create Redis client."""
        if self._redis_client is None and not self._init_complete:
            self._init_complete = True
            try:
                self._redis_client = redis.from_url(self.redis_url)
            except Exception as e:
                logger.warning(f"Failed to connect to Redis for rate limiting: {e}")
                return None
        return self._redis_client

    def _get_client_identifier(self, request: Request) -> str:
        """Extract client identifier (prefer X-Forwarded-For, fallback to client host)."""
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Take the first IP in the chain (original client)
            return forwarded_for.split(',')[0].strip()
        return request.client.host if request.client else 'unknown'

    def _is_exempt(self, request: Request) -> bool:
        """Check if request path is exempt from rate limiting."""
        return any(request.url.path.startswith(path) for path in self.exempt_paths)

    async def _check_rate_limit(self, client_id: str) -> tuple[bool, int, int, int]:
        """
        Check if request is within rate limit using sliding window.

        Returns:
            Tuple of (allowed, limit, remaining, reset_time)
        """
        redis_client = await self._get_redis_client()

        if redis_client is None:
            # Redis unavailable - allow request (fail open)
            logger.warning("Redis unavailable for rate limiting, allowing request")
            return True, self.requests_per_minute, self.requests_per_minute, 0

        try:
            now = time.time()
            window_start = now - self._window_size

            # Redis key for this client
            key = f"rate_limit:{client_id}"

            # Remove old entries outside the window
            await redis_client.zremrangebyscore(key, 0, window_start)

            # Count current requests in window
            current_requests = await redis_client.zcard(key)

            if current_requests >= self.requests_per_minute:
                # Rate limit exceeded
                # Get the oldest request to calculate reset time
                oldest = await redis_client.zrange(key, 0, 0, withscores=True)
                if oldest:
                    reset_time = int(oldest[0][1] + self._window_size)
                else:
                    reset_time = int(now + self._window_size)

                remaining = max(0, self.requests_per_minute - current_requests)
                return False, self.requests_per_minute, remaining, reset_time

            # Add current request to the window
            await redis_client.zadd(key, {str(now): now})

            # Set expiry on the key to auto-cleanup
            await redis_client.expire(key, self._window_size)

            # Calculate remaining requests and reset time
            remaining = self.requests_per_minute - (current_requests + 1)
            reset_time = int(now + self._window_size)

            return True, self.requests_per_minute, remaining, reset_time

        except Exception as e:
            # Redis error - log warning and allow request (fail open)
            logger.warning(f"Redis error during rate limit check: {e}")
            return True, self.requests_per_minute, self.requests_per_minute, 0

    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request with rate limiting."""
        # Skip rate limiting for exempt paths
        if self._is_exempt(request):
            return await call_next(request)

        # Get client identifier
        client_id = self._get_client_identifier(request)

        # Check rate limit
        allowed, limit, remaining, reset_time = await self._check_rate_limit(client_id)

        if not allowed:
            # Rate limit exceeded - return 429
            retry_after = max(1, reset_time - int(time.time()))

            response = Response(
                content='{"detail": "Rate limit exceeded"}',
                status_code=429,
                headers={
                    'Content-Type': 'application/json',
                    'X-RateLimit-Limit': str(limit),
                    'X-RateLimit-Remaining': str(remaining),
                    'X-RateLimit-Reset': str(reset_time),
                    'Retry-After': str(retry_after)
                }
            )
            return response

        # Process the request
        response = await call_next(request)

        # Add rate limit headers to response
        response.headers['X-RateLimit-Limit'] = str(limit)
        response.headers['X-RateLimit-Remaining'] = str(remaining)
        response.headers['X-RateLimit-Reset'] = str(reset_time)

        return response
