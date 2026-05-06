import logging
from typing import Optional

from elasticsearch import AsyncElasticsearch

from app.core.config import get_settings
from app.models.novel import Novel

logger = logging.getLogger(__name__)

es_client: Optional[AsyncElasticsearch] = None

NOVEL_INDEX = "novels"


async def get_es_client() -> AsyncElasticsearch:
    global es_client
    if es_client is None:
        settings = get_settings()
        es_client = AsyncElasticsearch(settings.ES_URL)
    return es_client


async def ensure_index():
    client = await get_es_client()
    exists = await client.indices.exists(index=NOVEL_INDEX)
    if not exists:
        mappings = {
            "properties": {
                "title": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "author": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
                "category": {"type": "keyword"},
                "description": {"type": "text", "analyzer": "ik_max_word", "search_analyzer": "ik_smart"},
            }
        }
        await client.indices.create(index=NOVEL_INDEX, mappings=mappings)
        logger.info("创建Elasticsearch索引: %s", NOVEL_INDEX)


async def index_novel(novel: Novel):
    client = await get_es_client()
    doc = {
        "title": novel.title,
        "author": novel.author,
        "category": novel.category,
        "description": novel.description or "",
    }
    await client.index(index=NOVEL_INDEX, id=str(novel.id), document=doc)
    logger.info("索引小说: %s (ID: %s)", novel.title, novel.id)


async def search_novels(query: str, size: int = 20) -> list[dict]:
    client = await get_es_client()
    result = await client.search(
        index=NOVEL_INDEX,
        query={
            "multi_match": {
                "query": query,
                "fields": ["title^3", "author^2", "description"],
            }
        },
        highlight={
            "fields": {
                "title": {},
                "description": {},
            }
        },
        size=size,
    )
    hits = result.get("hits", {}).get("hits", [])
    return [
        {
            "id": hit["_id"],
            "score": hit["_score"],
            "source": hit["_source"],
            "highlight": hit.get("highlight", {}),
        }
        for hit in hits
    ]


async def close_es():
    global es_client
    if es_client:
        await es_client.close()
        es_client = None
