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
    client = await get_redis()
    value = await client.get(key)
    if value:
        logger.debug("缓存命中: %s", key)
    return value


async def set_cached(key: str, value: Any, ttl: int = 300) -> None:
    client = await get_redis()
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False)
    await client.set(key, value, ex=ttl)
    logger.debug("设置缓存: %s (TTL=%d)", key, ttl)


async def delete_cached(key: str) -> None:
    client = await get_redis()
    await client.delete(key)


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None
