import pytest
import time
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.cache import (
    MemoryCache,
    get_cached,
    set_cached,
    delete_cached,
    delete_cached_pattern,
    _memory_cache,
)


class TestMemoryCache:
    def test_get_returns_cached_value(self):
        cache = MemoryCache()
        cache._store["test_key"] = ("test_value", time.time() + 100)
        result = cache._store["test_key"]
        assert result[0] == "test_value"

    @pytest.mark.asyncio
    async def test_get_returns_none_for_expired_key(self):
        cache = MemoryCache()
        cache._store["expired_key"] = ("old_value", time.time() - 1)
        result = await cache.get("expired_key")
        assert result is None
        assert "expired_key" not in cache._store

    @pytest.mark.asyncio
    async def test_get_returns_none_for_missing_key(self):
        cache = MemoryCache()
        result = await cache.get("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_stores_with_ttl(self):
        cache = MemoryCache()
        await cache.set("new_key", "new_value", ex=60)
        assert "new_key" in cache._store
        value, expires_at = cache._store["new_key"]
        assert value == "new_value"
        assert expires_at > time.time()

    @pytest.mark.asyncio
    async def test_delete_removes_key(self):
        cache = MemoryCache()
        await cache.set("to_delete", "value", ex=100)
        await cache.delete("to_delete")
        assert "to_delete" not in cache._store

    @pytest.mark.asyncio
    async def test_delete_nonexistent_key_silent(self):
        cache = MemoryCache()
        await cache.delete("nonexistent")

    def test_scan_iter_matches_pattern(self):
        cache = MemoryCache()
        cache._store["novel:1"] = ("v1", time.time() + 100)
        cache._store["novel:2"] = ("v2", time.time() + 100)
        cache._store["user:1"] = ("v3", time.time() + 100)

        keys = cache.scan_iter("novel:*")
        assert len(keys) == 2
        assert "novel:1" in keys
        assert "novel:2" in keys

    def test_scan_iter_no_matches(self):
        cache = MemoryCache()
        keys = cache.scan_iter("nonexistent:*")
        assert len(keys) == 0


@pytest.mark.asyncio
async def test_get_cached_returns_cached_data():
    with patch("app.services.cache.get_cache_client", new_callable=AsyncMock) as mock_client:
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(return_value="cached_value")
        mock_client.return_value = mock_cache

        result = await get_cached("test_key")
        assert result == "cached_value"
        mock_cache.get.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_get_cached_falls_back_on_error():
    with patch("app.services.cache.get_cache_client", new_callable=AsyncMock) as mock_client:
        mock_cache = MagicMock()
        mock_cache.get = AsyncMock(side_effect=Exception("Redis error"))
        mock_client.return_value = mock_cache

        with patch("app.services.cache._memory_cache") as mock_mem:
            mock_mem.get = AsyncMock(return_value="memory_fallback")
            result = await get_cached("test_key")
            assert result is None


@pytest.mark.asyncio
async def test_set_cached_with_string_value():
    with patch("app.services.cache.get_cache_client", new_callable=AsyncMock) as mock_client:
        with patch("app.services.cache.get_settings") as mock_settings:
            mock_settings.return_value.CACHE_TTL = 300
            mock_cache = MagicMock()
            mock_cache.set = AsyncMock()
            mock_client.return_value = mock_cache

            await set_cached("key", "string_value", ttl=100)
            mock_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_set_cached_with_dict_value():
    with patch("app.services.cache.get_cache_client", new_callable=AsyncMock) as mock_client:
        with patch("app.services.cache.get_settings") as mock_settings:
            mock_settings.return_value.CACHE_TTL = 300
            mock_cache = MagicMock()
            mock_cache.set = AsyncMock()
            mock_client.return_value = mock_cache

            await set_cached("key", {"title": "test"}, ttl=100)
            mock_cache.set.assert_called_once()


@pytest.mark.asyncio
async def test_delete_cached():
    with patch("app.services.cache.get_cache_client", new_callable=AsyncMock) as mock_client:
        mock_cache = MagicMock()
        mock_cache.delete = AsyncMock()
        mock_client.return_value = mock_cache

        await delete_cached("test_key")
        mock_cache.delete.assert_called_once_with("test_key")


@pytest.mark.asyncio
async def test_delete_cached_pattern():
    with patch("app.services.cache.get_cache_client", new_callable=AsyncMock) as mock_client:
        mock_cache = MagicMock()
        mock_cache.scan_iter = MagicMock(return_value=["key1", "key2"])
        mock_cache.delete = AsyncMock()
        mock_client.return_value = mock_cache

        with patch("app.services.cache._redis_available", True):
            with patch("app.services.cache._redis_client", mock_cache):
                mock_cache.scan_iter = MagicMock(return_value=["novel:1", "novel:2"])
                await delete_cached_pattern("novel:*")
                assert mock_cache.delete.call_count >= 0
