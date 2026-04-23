import json
import logging
from typing import Any

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)


class CacheBackend:
    """Redis-backed async caching for task queries."""

    def __init__(self, redis_url: str = None):
        self._redis_url = redis_url or settings.redis_url
        self._client: redis.Redis | None = None

    async def _get_client(self) -> redis.Redis | None:
        """Get or create Redis client."""
        if self._client is None:
            try:
                self._client = redis.from_url(self._redis_url)
            except Exception as e:
                logger.warning(f"Failed to connect to Redis: {e}")
                return None
        return self._client

    async def get(self, key: str) -> Any | None:
        """
        Retrieve cached value or None on miss.

        Returns deserialized value if found, None otherwise.
        Logs warning and returns None if Redis is unreachable.
        """
        client = await self._get_client()
        if client is None:
            logger.warning(f"Cache unavailable for get({key}), returning None")
            return None

        try:
            data = await client.get(key)
            if data is None:
                return None
            return json.loads(data)
        except Exception as e:
            logger.warning(f"Redis error on get({key}): {e}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """
        Store value with TTL (default 5 minutes).

        Returns True if successful, False otherwise.
        """
        client = await self._get_client()
        if client is None:
            logger.warning(f"Cache unavailable for set({key}), skipping cache")
            return False

        try:
            serialized = json.dumps(value)
            await client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.warning(f"Redis error on set({key}): {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Invalidate cached key.

        Returns True if successful, False otherwise.
        """
        client = await self._get_client()
        if client is None:
            logger.warning(f"Cache unavailable for delete({key}), skipping")
            return False

        try:
            await client.delete(key)
            return True
        except Exception as e:
            logger.warning(f"Redis error on delete({key}): {e}")
            return False

    async def health_check(self) -> bool:
        """
        Verify Redis connectivity.

        Returns True if Redis is reachable, False otherwise.
        """
        client = await self._get_client()
        if client is None:
            return False

        try:
            await client.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis health check failed: {e}")
            return False


# Singleton instance
cache = CacheBackend()
