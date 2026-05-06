import re
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator

from app.core.security import get_current_user
from app.models.user import User
from app.services.crawler_client import crawler_client

router = APIRouter(prefix="/api/crawler", tags=["爬虫"])

_URL_PATTERN = re.compile(r"^https?://[^\s/$.?#].[^\s]*$")


class CrawlRequest(BaseModel):
    source_id: str
    novel_url: str

    @field_validator("source_id")
    @classmethod
    def validate_source_id(cls, v: str) -> str:
        if not v or len(v) > 100:
            raise ValueError("source_id 不能为空且长度不能超过100")
        if not re.match(r"^[\w\-]+$", v):
            raise ValueError("source_id 只能包含字母、数字、下划线和连字符")
        return v

    @field_validator("novel_url")
    @classmethod
    def validate_novel_url(cls, v: str) -> str:
        if not v or len(v) > 2048:
            raise ValueError("novel_url 不能为空且长度不能超过2048")
        if not _URL_PATTERN.match(v):
            raise ValueError("novel_url 必须是有效的 HTTP/HTTPS URL")
        parsed = urlparse(v)
        if not parsed.scheme or not parsed.netloc:
            raise ValueError("novel_url 格式不正确")
        return v


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
    if not re.match(r"^[\w\-]+$", source_id) or len(source_id) > 100:
        raise HTTPException(status_code=400, detail="无效的 source_id")
    result = await crawler_client.get_status(source_id)
    return result


@router.get("/sources")
async def list_sources(
    current_user: User = Depends(get_current_user),
):
    sources = await crawler_client.list_sources()
    return {"sources": sources}
