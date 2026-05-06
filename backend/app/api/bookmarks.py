import json
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.novel import Novel
from app.models.chapter import Chapter
from app.models.advanced import Bookmark, ReadingStats
from app.schemas.advanced import (
    BookmarkCreate,
    BookmarkResponse,
    ReadingStatsResponse,
    ReadingStatsSummary,
)
from app.services.cache import get_cached, set_cached, delete_cached

router = APIRouter(prefix="/api/bookmarks", tags=["收藏"])


@router.get("", response_model=list[BookmarkResponse])
async def list_bookmarks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bookmark)
        .where(Bookmark.user_id == current_user.id)
        .order_by(Bookmark.created_at.desc())
    )
    return result.scalars().all()


@router.post("", response_model=BookmarkResponse, status_code=201)
async def create_bookmark(
    data: BookmarkCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Novel).where(Novel.id == data.novel_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="小说不存在")

    existing = await db.execute(
        select(Bookmark).where(
            Bookmark.user_id == current_user.id,
            Bookmark.novel_id == data.novel_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="已收藏该小说")

    bookmark = Bookmark(
        user_id=current_user.id,
        novel_id=data.novel_id,
        note=data.note,
    )
    db.add(bookmark)
    await db.flush()
    return bookmark


@router.delete("/{bookmark_id}", status_code=204)
async def delete_bookmark(
    bookmark_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.id == bookmark_id,
            Bookmark.user_id == current_user.id,
        )
    )
    bookmark = result.scalar_one_or_none()
    if not bookmark:
        raise HTTPException(status_code=404, detail="收藏不存在")
    await db.execute(delete(Bookmark).where(Bookmark.id == bookmark_id))


@router.get("/check/{novel_id}")
async def check_bookmark(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Bookmark).where(
            Bookmark.user_id == current_user.id,
            Bookmark.novel_id == novel_id,
        )
    )
    return {"bookmarked": result.scalar_one_or_none() is not None}


@router.get("/stats", response_model=ReadingStatsSummary)
async def get_reading_stats(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"stats:{current_user.id}:{days}"
    cached = await get_cached(cache_key)
    if cached:
        return json.loads(cached)

    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    result = await db.execute(
        select(ReadingStats)
        .where(
            ReadingStats.user_id == current_user.id,
            ReadingStats.date >= start_date,
        )
        .order_by(ReadingStats.date)
    )
    daily_stats = result.scalars().all()

    total_chapters = sum(s.chapters_read for s in daily_stats)
    total_words = sum(s.words_read for s in daily_stats)
    total_minutes = sum(s.reading_minutes for s in daily_stats)

    streak = 0
    today = datetime.now(timezone.utc).date()
    for i in range(days):
        check_date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        found = any(s.date == check_date for s in daily_stats)
        if found:
            streak += 1
        elif i > 0:
            break

    summary = ReadingStatsSummary(
        total_chapters=total_chapters,
        total_words=total_words,
        total_minutes=total_minutes,
        streak_days=streak,
        daily_stats=[ReadingStatsResponse.model_validate(s) for s in daily_stats],
    )

    await set_cached(cache_key, summary.model_dump(mode="json"), ttl=60)
    return summary
