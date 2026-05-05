from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.security import get_current_user
from app.models.user import User
from app.services.crawler_client import crawler_client

router = APIRouter(prefix="/api/crawler", tags=["爬虫"])


class CrawlRequest(BaseModel):
    source_id: str
    novel_url: str


@router.post("/start")
async def start_crawl(
    req: CrawlRequest,
    current_user: User = Depends(get_current_user),
):
    result = await crawler_client.start_crawl(req.source_id, req.novel_url)
    return result


@router.get("/status")
async def get_crawler_status(
    source_id: str = "default",
    current_user: User = Depends(get_current_user),
):
    result = await crawler_client.get_status(source_id)
    return result


@router.get("/sources")
async def list_sources(
    current_user: User = Depends(get_current_user),
):
    sources = await crawler_client.list_sources()
    return {"sources": sources}
