import pytest
import asyncio

from app.services.cache import (
    MemoryCache,
    get_cached,
    set_cached,
    delete_cached,
    delete_cached_pattern,
)


class TestMemoryCache:
    def test_memory_cache_get_set(self):
        cache = MemoryCache()
        asyncio.run(cache.set("key1", "value1", ex=300))

        result = asyncio.run(cache.get("key1"))
        assert result == "value1"

    def test_memory_cache_get_expired(self):
        cache = MemoryCache()
        asyncio.run(cache.set("expired_key", "value", ex=0))

        result = asyncio.run(cache.get("expired_key"))
        assert result is None

    def test_memory_cache_delete(self):
        cache = MemoryCache()
        asyncio.run(cache.set("delete_key", "value", ex=300))
        asyncio.run(cache.delete("delete_key"))

        result = asyncio.run(cache.get("delete_key"))
        assert result is None

    def test_memory_cache_scan_iter(self):
        cache = MemoryCache()
        asyncio.run(cache.set("novel:1", "data1", ex=300))
        asyncio.run(cache.set("novel:2", "data2", ex=300))
        asyncio.run(cache.set("user:1", "user_data", ex=300))

        keys = cache.scan_iter(match="novel:*")
        assert len(keys) == 2
        assert "novel:1" in keys
        assert "novel:2" in keys

        keys = cache.scan_iter(match="user:*")
        assert len(keys) == 1
        assert "user:1" in keys

    def test_memory_cache_scan_iter_wildcard(self):
        cache = MemoryCache()
        asyncio.run(cache.set("a:1", "v1", ex=300))
        asyncio.run(cache.set("a:2", "v2", ex=300))
        asyncio.run(cache.set("b:1", "v3", ex=300))

        keys = cache.scan_iter(match="*")
        assert len(keys) == 3

    def test_memory_cache_clear(self):
        cache = MemoryCache()
        asyncio.run(cache.set("key1", "value1", ex=300))
        asyncio.run(cache.set("key2", "value2", ex=300))
        asyncio.run(cache.close())

        result = asyncio.run(cache.get("key1"))
        assert result is None


class TestCacheFunctions:
    @pytest.mark.asyncio
    async def test_set_and_get_cached(self):
        await set_cached("test_key", "test_value", ttl=60)
        result = await get_cached("test_key")
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_get_cached_not_found(self):
        result = await get_cached("nonexistent_key_12345")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_cached_with_dict(self):
        test_data = {"name": "test", "value": 123}
        await set_cached("dict_key", test_data, ttl=60)

        result = await get_cached("dict_key")
        assert result is not None

    @pytest.mark.asyncio
    async def test_set_cached_with_list(self):
        test_data = [1, 2, 3, "test"]
        await set_cached("list_key", test_data, ttl=60)

        result = await get_cached("list_key")
        assert result is not None

    @pytest.mark.asyncio
    async def test_delete_cached(self):
        await set_cached("delete_test_key", "value", ttl=60)
        await delete_cached("delete_test_key")

        result = await get_cached("delete_test_key")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_cached_pattern(self):
        await set_cached("pattern:1", "value1", ttl=60)
        await set_cached("pattern:2", "value2", ttl=60)
        await set_cached("other:1", "value3", ttl=60)

        await delete_cached_pattern("pattern:*")

        result1 = await get_cached("pattern:1")
        result2 = await get_cached("pattern:2")
        result3 = await get_cached("other:1")

        assert result1 is None
        assert result2 is None
        assert result3 is not None

    @pytest.mark.asyncio
    async def test_cache_overwrite(self):
        await set_cached("overwrite_key", "original", ttl=60)
        await set_cached("overwrite_key", "updated", ttl=60)

        result = await get_cached("overwrite_key")
        assert result == "updated"
