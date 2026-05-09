import pytest
import time
import json

from app.services.cache import (
    MemoryCache,
    get_cached,
    set_cached,
    delete_cached,
    delete_cached_pattern,
)


class TestMemoryCache:
    def test_set_and_get(self):
        cache = MemoryCache()
        cache.run_sync = lambda: None

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test():
            await cache.set("key1", "value1")
            result = await cache.get("key1")
            assert result == "value1"

        loop.run_until_complete(test())
        loop.close()

    def test_get_nonexistent_key(self):
        cache = MemoryCache()

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test():
            result = await cache.get("nonexistent")
            assert result is None

        loop.run_until_complete(test())
        loop.close()

    def test_expiration(self):
        cache = MemoryCache()

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test():
            await cache.set("expiring_key", "value", ex=1)
            result = await cache.get("expiring_key")
            assert result == "value"

            time.sleep(1.1)
            result = await cache.get("expiring_key")
            assert result is None

        loop.run_until_complete(test())
        loop.close()

    def test_delete(self):
        cache = MemoryCache()

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test():
            await cache.set("to_delete", "value")
            await cache.delete("to_delete")
            result = await cache.get("to_delete")
            assert result is None

        loop.run_until_complete(test())
        loop.close()

    def test_scan_iter(self):
        cache = MemoryCache()

        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def test():
            await cache.set("user:1", "data1")
            await cache.set("user:2", "data2")
            await cache.set("post:1", "data3")

            user_keys = list(cache.scan_iter("user:*"))
            assert len(user_keys) == 2
            assert "user:1" in user_keys
            assert "user:2" in user_keys

            all_keys = list(cache.scan_iter("*"))
            assert len(all_keys) == 3

        loop.run_until_complete(test())
        loop.close()


class TestCacheIntegration:
    @pytest.mark.asyncio
    async def test_set_and_get_cached(self):
        await set_cached("test_key", "test_value")
        result = await get_cached("test_key")
        assert result == "test_value"

    @pytest.mark.asyncio
    async def test_get_nonexistent(self):
        result = await get_cached("nonexistent_key_12345")
        assert result is None

    @pytest.mark.asyncio
    async def test_set_dict_value(self):
        data = {"name": "test", "count": 42}
        await set_cached("dict_key", data)

        result = await get_cached("dict_key")
        assert result is not None
        parsed = json.loads(result)
        assert parsed["name"] == "test"
        assert parsed["count"] == 42

    @pytest.mark.asyncio
    async def test_delete_cached(self):
        await set_cached("to_delete", "value")
        await delete_cached("to_delete")
        result = await get_cached("to_delete")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_cached_pattern(self):
        await set_cached("pattern:1", "v1")
        await set_cached("pattern:2", "v2")
        await set_cached("other:1", "v3")

        await delete_cached_pattern("pattern:*")

        result1 = await get_cached("pattern:1")
        result2 = await get_cached("pattern:2")
        result3 = await get_cached("other:1")

        assert result1 is None
        assert result2 is None
        assert result3 is not None

    @pytest.mark.asyncio
    async def test_ttl_respected(self):
        import asyncio

        await set_cached("ttl_test", "value", ttl=1)
        result1 = await get_cached("ttl_test")
        assert result1 == "value"

        await asyncio.sleep(1.1)
        result2 = await get_cached("ttl_test")
        assert result2 is None

    @pytest.mark.asyncio
    async def test_overwrite_existing(self):
        await set_cached("overwrite", "first")
        await set_cached("overwrite", "second")

        result = await get_cached("overwrite")
        assert result == "second"

    @pytest.mark.asyncio
    async def test_json_serializable_list(self):
        data = [1, 2, 3, "test"]
        await set_cached("list_key", data)

        result = await get_cached("list_key")
        parsed = json.loads(result)
        assert parsed == data
