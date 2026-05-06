import json
import logging
from typing import Optional, Any

import redis.asyncio as aioredis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

redis_client: Optional[aioredis.Redis] = None


async def get_redis() -> aioredis.Redis:
    global redis_client
    if redis_client is None:
        settings = get_settings()
        redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    return redis_client


async def get_cached(key: str) -> Optional[str]:
    try:
        client = await get_redis()
        value = await client.get(key)
        if value:
            logger.debug("缓存命中: %s", key)
        return value
    except Exception as e:
        logger.warning("缓存读取失败: %s - %s", key, e)
        return None


async def set_cached(key: str, value: Any, ttl: int = 300) -> None:
    try:
        client = await get_redis()
        if isinstance(value, str):
            serialized = value
        else:
            serialized = json.dumps(value, ensure_ascii=False, default=str)
        await client.set(key, serialized, ex=ttl)
        logger.debug("设置缓存: %s (TTL=%d)", key, ttl)
    except Exception as e:
        logger.warning("缓存写入失败: %s - %s", key, e)


async def delete_cached(key: str) -> None:
    try:
        client = await get_redis()
        await client.delete(key)
    except Exception as e:
        logger.warning("缓存删除失败: %s - %s", key, e)


async def delete_cached_pattern(pattern: str) -> None:
    try:
        client = await get_redis()
        async for key in client.scan_iter(match=pattern):
            await client.delete(key)
    except Exception as e:
        logger.warning("缓存模式删除失败: %s - %s", pattern, e)


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
