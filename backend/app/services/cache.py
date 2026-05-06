import json
import time
import logging
from typing import Optional, Any

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_redis_client = None
_redis_available: Optional[bool] = None
_memory_cache: dict[str, tuple[Any, float]] = {}


class MemoryCache:
    def __init__(self):
        self._store: dict[str, tuple[Any, float]] = {}

    async def get(self, key: str) -> Optional[str]:
        if key in self._store:
            value, expires_at = self._store[key]
            if time.time() < expires_at:
                return value
            del self._store[key]
        return None

    async def set(self, key: str, value: str, ex: int = 300) -> None:
        self._store[key] = (value, time.time() + ex)

    async def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def scan_iter(self, match: str = "*"):
        import fnmatch
        keys = list(self._store.keys())
        return [k for k in keys if fnmatch.fnmatch(k, match)]

    async def close(self) -> None:
        self._store.clear()


_memory_cache = MemoryCache()


async def _try_connect_redis():
    global _redis_client, _redis_available
    settings = get_settings()
    try:
        import redis.asyncio as aioredis
        _redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
        await _redis_client.ping()
        _redis_available = True
        logger.info("Redis 连接成功: %s", settings.REDIS_URL)
    except Exception as e:
        _redis_available = False
        _redis_client = None
        logger.warning("Redis 连接失败，使用内存缓存: %s", e)


async def get_cache_client():
    if _redis_available and _redis_client:
        return _redis_client
    return _memory_cache


async def get_cached(key: str) -> Optional[str]:
    try:
        client = await get_cache_client()
        value = await client.get(key)
        if value:
            logger.debug("缓存命中: %s", key)
        return value
    except Exception as e:
        logger.warning("缓存读取失败: %s - %s", key, e)
        if _redis_available:
            try:
                return await _memory_cache.get(key)
            except Exception:
                pass
        return None


async def set_cached(key: str, value: Any, ttl: int = 0) -> None:
    settings = get_settings()
    if ttl <= 0:
        ttl = settings.CACHE_TTL
    try:
        client = await get_cache_client()
        if isinstance(value, str):
            serialized = value
        else:
            serialized = json.dumps(value, ensure_ascii=False, default=str)
        await client.set(key, serialized, ex=ttl)
        logger.debug("设置缓存: %s (TTL=%d)", key, ttl)
    except Exception as e:
        logger.warning("缓存写入失败: %s - %s", key, e)
        try:
            if isinstance(value, str):
                await _memory_cache.set(key, value, ex=ttl)
            else:
                await _memory_cache.set(key, json.dumps(value, ensure_ascii=False, default=str), ex=ttl)
        except Exception:
            pass


async def delete_cached(key: str) -> None:
    try:
        client = await get_cache_client()
        await client.delete(key)
    except Exception as e:
        logger.warning("缓存删除失败: %s - %s", key, e)


async def delete_cached_pattern(pattern: str) -> None:
    try:
        client = await get_cache_client()
        if _redis_available and _redis_client:
            async for key in _redis_client.scan_iter(match=pattern):
                await _redis_client.delete(key)
        else:
            keys = _memory_cache.scan_iter(match=pattern)
            for key in keys:
                await _memory_cache.delete(key)
    except Exception as e:
        logger.warning("缓存模式删除失败: %s - %s", pattern, e)


async def init_cache():
    await _try_connect_redis()


async def close_redis():
    global _redis_client, _redis_available
    if _redis_client:
        await _redis_client.close()
        _redis_client = None
    await _memory_cache.close()
    _redis_available = None
