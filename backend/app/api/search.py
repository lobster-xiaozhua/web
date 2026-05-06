from fastapi import APIRouter, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import Depends
from app.db.database import get_db
from app.models.novel import Novel
from app.services.search_service import search_novels, index_novel

router = APIRouter(prefix="/api/search", tags=["搜索"])


@router.get("")
async def search(
    q: str = Query(..., min_length=1, max_length=200),
    size: int = Query(20, ge=1, le=100),
):
    results = await search_novels(query=q, size=size)
    return {"query": q, "total": len(results), "results": results}
