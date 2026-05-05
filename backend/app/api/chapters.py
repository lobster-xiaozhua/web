import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.novel import Novel
from app.models.chapter import Chapter
from app.models.reading_progress import ReadingProgress
from app.schemas.chapter import (
    ChapterContentResponse,
    ReadingProgressCreate,
    ReadingProgressResponse,
)
from app.services.book_loader import _decompress_content
from app.services.cache import get_cached, set_cached

router = APIRouter(prefix="/api/novels", tags=["章节"])


@router.get("/{novel_id}/chapters/{chapter_index}", response_model=ChapterContentResponse)
async def get_chapter_content(
    novel_id: uuid.UUID,
    chapter_index: int,
    db: AsyncSession = Depends(get_db),
):
    cache_key = f"chapter:{novel_id}:{chapter_index}"
    cached = await get_cached(cache_key)
    if cached:
        return json.loads(cached)

    result = await db.execute(
        select(Chapter).where(
            Chapter.novel_id == novel_id,
            Chapter.chapter_index == chapter_index,
        )
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="章节不存在")

    content_text = ""
    if chapter.content:
        content_text = _decompress_content(chapter.content)

    response = ChapterContentResponse(
        id=chapter.id,
        novel_id=chapter.novel_id,
        title=chapter.title,
        chapter_index=chapter.chapter_index,
        content=content_text,
        word_count=chapter.word_count,
        created_at=chapter.created_at,
    )

    await set_cached(
        cache_key,
        response.model_dump(mode="json"),
        ttl=600,
    )
    return response


@router.post("/{novel_id}/progress", response_model=ReadingProgressResponse)
async def update_reading_progress(
    novel_id: uuid.UUID,
    progress_in: ReadingProgressCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ReadingProgress).where(
            ReadingProgress.user_id == current_user.id,
            ReadingProgress.novel_id == novel_id,
        )
    )
    progress = result.scalar_one_or_none()

    if progress:
        progress.chapter_id = progress_in.chapter_id
        progress.progress_percent = progress_in.progress_percent
        progress.last_read_at = datetime.now(timezone.utc)
        await db.flush()
    else:
        progress = ReadingProgress(
            user_id=current_user.id,
            novel_id=novel_id,
            chapter_id=progress_in.chapter_id,
            progress_percent=progress_in.progress_percent,
        )
        db.add(progress)
        await db.flush()

    return progress


@router.get("/{novel_id}/progress", response_model=ReadingProgressResponse)
async def get_reading_progress(
    novel_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ReadingProgress).where(
            ReadingProgress.user_id == current_user.id,
            ReadingProgress.novel_id == novel_id,
        )
    )
    progress = result.scalar_one_or_none()
    if not progress:
        raise HTTPException(status_code=404, detail="暂无阅读进度")
    return progress
