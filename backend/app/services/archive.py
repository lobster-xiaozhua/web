import logging
from datetime import datetime, timezone, timedelta

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel, NovelStatus
from app.models.chapter import Chapter, ArchivedChapter

logger = logging.getLogger(__name__)


async def archive_old_novels(session: AsyncSession) -> int:
    one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)

    result = await session.execute(
        select(Novel).where(
            Novel.status == NovelStatus.completed,
            Novel.updated_at < one_year_ago,
        )
    )
    old_novels = result.scalars().all()

    archived_count = 0

    for novel in old_novels:
        chapters_result = await session.execute(
            select(Chapter).where(Chapter.novel_id == novel.id)
        )
        chapters = chapters_result.scalars().all()

        for chapter in chapters:
            archived = ArchivedChapter(
                id=chapter.id,
                novel_id=chapter.novel_id,
                title=chapter.title,
                chapter_index=chapter.chapter_index,
                content=chapter.content,
                content_hash=chapter.content_hash,
                simhash=chapter.simhash,
                word_count=chapter.word_count,
                created_at=chapter.created_at,
            )
            session.add(archived)

        await session.execute(delete(Chapter).where(Chapter.novel_id == novel.id))
        archived_count += len(chapters)
        logger.info("归档小说: %s (共 %d 章)", novel.title, len(chapters))

    if archived_count > 0:
        await session.flush()

    logger.info("归档完成，共迁移 %d 个章节", archived_count)
    return archived_count
