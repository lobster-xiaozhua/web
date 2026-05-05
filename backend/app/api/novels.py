import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.novel import Novel, NovelStatus
from app.models.chapter import Chapter
from app.schemas.novel import (
    NovelResponse,
    NovelListResponse,
    NovelDetailResponse,
    ChapterBrief,
)
from app.services.cache import get_cached, set_cached

router = APIRouter(prefix="/api/novels", tags=["小说"])


@router.get("/categories", response_model=list[str])
async def get_categories(db: AsyncSession = Depends(get_db)):
    cached = await get_cached("novel:categories")
    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(Novel.category).distinct().order_by(Novel.category)
    )
    categories = [row[0] for row in result.all()]
    await set_cached("novel:categories", categories, ttl=600)
    return categories


@router.get("/recommended", response_model=list[NovelResponse])
async def get_recommended(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    cached = await get_cached("novel:recommended")
    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(Novel).order_by(Novel.rating.desc()).limit(limit)
    )
    novels = result.scalars().all()
    response = [NovelResponse.model_validate(n) for n in novels]
    await set_cached("novel:recommended", [r.model_dump(mode="json") for r in response], ttl=300)
    return response


@router.get("", response_model=NovelListResponse)
async def list_novels(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: str | None = Query(None),
    status: NovelStatus | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Novel)
    count_query = select(func.count(Novel.id))

    if category:
        query = query.where(Novel.category == category)
        count_query = count_query.where(Novel.category == category)
    if status:
        query = query.where(Novel.status == status)
        count_query = count_query.where(Novel.status == status)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(
        query.order_by(Novel.updated_at.desc()).offset(offset).limit(page_size)
    )
    novels = result.scalars().all()

    return NovelListResponse(
        total=total,
        items=[NovelResponse.model_validate(n) for n in novels],
        page=page,
        page_size=page_size,
    )


@router.get("/{novel_id}", response_model=NovelDetailResponse)
async def get_novel(
    novel_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Novel).where(Novel.id == novel_id))
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    chapters_result = await db.execute(
        select(Chapter)
        .where(Chapter.novel_id == novel_id)
        .order_by(Chapter.chapter_index)
    )
    chapters = chapters_result.scalars().all()

    return NovelDetailResponse(
        **NovelResponse.model_validate(novel).model_dump(),
        chapters=[ChapterBrief.model_validate(c) for c in chapters],
    )
