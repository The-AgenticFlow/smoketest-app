import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.cache import CacheBackend
from app.routes import CACHE_KEY_TASKS_ALL, list_tasks


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client."""
    client = MagicMock()
    client.get = AsyncMock()
    client.setex = AsyncMock()
    client.delete = AsyncMock()
    client.ping = AsyncMock()
    return client


@pytest.fixture
def cache_backend(mock_redis_client):
    """Create a CacheBackend with mocked Redis client."""
    backend = CacheBackend(redis_url="redis://localhost:6379/0")
    backend._client = mock_redis_client
    return backend


class TestCacheBackend:
    """Test the CacheBackend class."""

    @pytest.mark.anyio
    async def test_get_returns_value_on_cache_hit(self, cache_backend, mock_redis_client):
        """Test get() returns deserialized value when key exists."""
        # Setup
        data = [{"id": 1, "title": "Task 1", "completed": False}]
        mock_redis_client.get.return_value = json.dumps(data)

        # Execute
        result = await cache_backend.get("tasks:all")

        # Assert
        assert result == data
        mock_redis_client.get.assert_called_once_with("tasks:all")

    @pytest.mark.anyio
    async def test_get_returns_none_on_cache_miss(self, cache_backend, mock_redis_client):
        """Test get() returns None when key doesn't exist."""
        # Setup
        mock_redis_client.get.return_value = None

        # Execute
        result = await cache_backend.get("tasks:all")

        # Assert
        assert result is None

    @pytest.mark.anyio
    async def test_get_returns_none_on_redis_error(self, cache_backend, mock_redis_client):
        """Test get() returns None when Redis raises an exception."""
        # Setup
        mock_redis_client.get.side_effect = Exception("Connection refused")

        # Execute
        result = await cache_backend.get("tasks:all")

        # Assert
        assert result is None

    @pytest.mark.anyio
    async def test_set_stores_value_with_ttl(self, cache_backend, mock_redis_client):
        """Test set() serializes and stores value with TTL."""
        # Setup
        data = [{"id": 1, "title": "Task 1", "completed": False}]

        # Execute
        result = await cache_backend.set("tasks:all", data, ttl=300)

        # Assert
        assert result is True
        mock_redis_client.setex.assert_called_once_with(
            "tasks:all", 300, json.dumps(data)
        )

    @pytest.mark.anyio
    async def test_set_returns_false_on_redis_error(self, cache_backend, mock_redis_client):
        """Test set() returns False when Redis raises an exception."""
        # Setup
        mock_redis_client.setex.side_effect = Exception("Connection refused")

        # Execute
        result = await cache_backend.set("tasks:all", [])

        # Assert
        assert result is False

    @pytest.mark.anyio
    async def test_delete_removes_key(self, cache_backend, mock_redis_client):
        """Test delete() removes the key from Redis."""
        # Execute
        result = await cache_backend.delete("tasks:all")

        # Assert
        assert result is True
        mock_redis_client.delete.assert_called_once_with("tasks:all")

    @pytest.mark.anyio
    async def test_delete_returns_false_on_redis_error(self, cache_backend, mock_redis_client):
        """Test delete() returns False when Redis raises an exception."""
        # Setup
        mock_redis_client.delete.side_effect = Exception("Connection refused")

        # Execute
        result = await cache_backend.delete("tasks:all")

        # Assert
        assert result is False

    @pytest.mark.anyio
    async def test_health_check_returns_true_when_reachable(self, cache_backend, mock_redis_client):
        """Test health_check() returns True when Redis responds to ping."""
        # Setup
        mock_redis_client.ping.return_value = True

        # Execute
        result = await cache_backend.health_check()

        # Assert
        assert result is True
        mock_redis_client.ping.assert_called_once()

    @pytest.mark.anyio
    async def test_health_check_returns_false_when_unreachable(
        self, cache_backend, mock_redis_client
    ):
        """Test health_check() returns False when Redis ping fails."""
        # Setup
        mock_redis_client.ping.side_effect = Exception("Connection refused")

        # Execute
        result = await cache_backend.health_check()

        # Assert
        assert result is False

    @pytest.mark.anyio
    async def test_graceful_degradation_when_client_none(self, cache_backend):
        """Test all methods work when Redis client is None (unreachable)."""
        # Setup
        cache_backend._client = None

        # Mock from_url to return None (connection failure)
        with patch("app.cache.redis.from_url", side_effect=Exception("Cannot connect")):
            # Execute & Assert - should not raise exceptions
            assert await cache_backend.get("key") is None
            assert await cache_backend.set("key", "value") is False
            assert await cache_backend.delete("key") is False
            assert await cache_backend.health_check() is False


class TestCacheIntegration:
    """Test cache integration with route scenarios."""

    @pytest.mark.anyio
    @patch("app.routes.cache")
    async def test_list_tasks_uses_cache_on_hit(self, mock_cache):
        """Test that list_tasks returns cached data when available."""
        # Setup mock cache with data
        cached_data = [{"id": 1, "title": "Cached Task", "completed": False, "priority": "medium"}]
        mock_cache.get = AsyncMock(return_value=cached_data)
        mock_cache.set = AsyncMock(return_value=True)

        # Call list_tasks - should return cached data without hitting DB
        result = await list_tasks()

        # Verify cache was checked
        mock_cache.get.assert_called_once_with(CACHE_KEY_TASKS_ALL)

        # Verify result is the cached data
        assert result == cached_data

        # Verify cache set was NOT called (we had a hit)
        mock_cache.set.assert_not_called()
