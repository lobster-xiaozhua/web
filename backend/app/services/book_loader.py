import os
import re
import hashlib
import logging
import asyncio
from pathlib import Path
from typing import Optional

import aiofiles
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent, FileModifiedEvent

from app.core.config import get_settings
from app.db.database import async_session
from app.models.novel import Novel
from app.models.chapter import Chapter

logger = logging.getLogger(__name__)

CHAPTER_PATTERN = re.compile(r"第(\d+)章[_\s](.+)\.txt$")

_event_loop: Optional[asyncio.AbstractEventLoop] = None


def _compress_content(text: str) -> bytes:
    try:
        from compressor import compress
        return compress(text.encode("utf-8"))
    except ImportError:
        import zlib
        return zlib.compress(text.encode("utf-8"), level=6)


def _decompress_content(data: bytes) -> str:
    try:
        from compressor import decompress
        return decompress(data).decode("utf-8")
    except ImportError:
        import zlib
        return zlib.decompress(data).decode("utf-8")


def _compute_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_chapter_filename(filename: str) -> Optional[tuple[int, str]]:
    match = CHAPTER_PATTERN.match(filename)
    if match:
        chapter_index = int(match.group(1))
        title = match.group(2).strip()
        return chapter_index, title
    return None


async def scan_books_dir() -> list[Novel]:
    settings = get_settings()
    books_path = Path(settings.BOOKS_DIR)
    if not books_path.exists():
        logger.warning("books目录不存在: %s", books_path)
        return []

    loaded_novels: list[Novel] = []

    async with async_session() as session:
        for novel_dir in sorted(books_path.iterdir()):
            if not novel_dir.is_dir():
                continue
            novel = await load_novel_from_dir(session, novel_dir)
            if novel:
                loaded_novels.append(novel)
        await session.commit()

    logger.info("扫描完成，共加载 %d 部小说", len(loaded_novels))
    return loaded_novels


async def load_novel_from_dir(session: AsyncSession, novel_dir: Path) -> Optional[Novel]:
    dir_name = novel_dir.name

    result = await session.execute(select(Novel).where(Novel.title == dir_name))
    novel = result.scalar_one_or_none()

    if novel is None:
        novel = Novel(
            title=dir_name,
            author="本地导入",
            category="未分类",
        )
        session.add(novel)
        await session.flush()
        logger.info("新建小说: %s", dir_name)

    for chapter_file in sorted(novel_dir.glob("*.txt")):
        await load_chapter_from_file(session, novel.id, chapter_file)

    await session.refresh(novel)
    total_result = await session.execute(
        select(func.coalesce(func.sum(Chapter.word_count), 0)).where(
            Chapter.novel_id == novel.id
        )
    )
    novel.total_words = total_result.scalar() or 0
    await session.flush()

    return novel


async def load_chapter_from_file(session: AsyncSession, novel_id, file_path: Path) -> Optional[Chapter]:
    parsed = parse_chapter_filename(file_path.name)
    if parsed is None:
        logger.debug("跳过无法解析的文件: %s", file_path.name)
        return None

    chapter_index, title = parsed

    result = await session.execute(
        select(Chapter).where(
            Chapter.novel_id == novel_id,
            Chapter.chapter_index == chapter_index,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
        content_text = await f.read()

    content_hash = _compute_content_hash(content_text)
    compressed = _compress_content(content_text)
    word_count = len(content_text.replace("\n", "").replace(" ", ""))

    chapter = Chapter(
        novel_id=novel_id,
        title=title,
        chapter_index=chapter_index,
        content=compressed,
        content_hash=content_hash,
        word_count=word_count,
    )
    session.add(chapter)
    await session.flush()
    logger.info("加载章节: 第%d章 %s (小说ID: %s)", chapter_index, title, novel_id)
    return chapter


class BooksDirHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".txt"):
            return
        logger.info("检测到新文件: %s", event.src_path)
        if _event_loop is not None and _event_loop.is_running():
            _event_loop.call_soon_threadsafe(
                lambda: asyncio.ensure_future(self._handle_file(event.src_path), loop=_event_loop)
            )
        else:
            logger.warning("事件循环不可用，跳过文件处理: %s", event.src_path)

    def on_modified(self, event):
        if event.is_directory:
            return
        if not event.src_path.endswith(".txt"):
            return
        logger.info("检测到文件修改: %s", event.src_path)

    async def _handle_file(self, file_path: str):
        path = Path(file_path)
        novel_dir = path.parent
        dir_name = novel_dir.name

        async with async_session() as session:
            result = await session.execute(select(Novel).where(Novel.title == dir_name))
            novel = result.scalar_one_or_none()
            if novel is None:
                novel = Novel(
                    title=dir_name,
                    author="本地导入",
                    category="未分类",
                )
                session.add(novel)
                await session.flush()
            await load_chapter_from_file(session, novel.id, path)
            await session.commit()


def start_watching() -> Observer:
    global _event_loop
    settings = get_settings()
    books_path = Path(settings.BOOKS_DIR)
    if not books_path.exists():
        books_path.mkdir(parents=True, exist_ok=True)

    _event_loop = asyncio.get_running_loop()

    observer = Observer()
    handler = BooksDirHandler()
    observer.schedule(handler, str(books_path), recursive=True)
    observer.daemon = True
    observer.start()
    logger.info("开始监控books目录: %s", books_path)
    return observer
