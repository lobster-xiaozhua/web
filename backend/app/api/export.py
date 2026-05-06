import io
import json
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user
from app.db.database import get_db
from app.models.user import User
from app.models.novel import Novel
from app.models.chapter import Chapter
from app.schemas.advanced import ExportRequest, BatchImportResponse, BatchImportRequest as ImportReq
from app.services.book_loader import _decompress_content, load_novel_from_dir
from app.services.cache import delete_cached_pattern

router = APIRouter(prefix="/api/export", tags=["导出"])


@router.post("/novel")
async def export_novel(
    data: ExportRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Novel).where(Novel.id == data.novel_id))
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="小说不存在")

    chapters_result = await db.execute(
        select(Chapter)
        .where(Chapter.novel_id == data.novel_id)
        .order_by(Chapter.chapter_index)
    )
    chapters = chapters_result.scalars().all()

    if data.chapter_range:
        try:
            parts = data.chapter_range.split("-")
            start = int(parts[0])
            end = int(parts[1]) if len(parts) > 1 else start
            chapters = [c for c in chapters if start <= c.chapter_index <= end]
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="章节范围格式错误，示例: 1-10")

    if data.format == "json":
        export_data = {
            "title": novel.title,
            "author": novel.author,
            "category": novel.category,
            "chapters": [],
        }
        for ch in chapters:
            content = _decompress_content(ch.content) if ch.content else ""
            export_data["chapters"].append({
                "index": ch.chapter_index,
                "title": ch.title,
                "content": content,
                "word_count": ch.word_count,
            })
        content_bytes = json.dumps(export_data, ensure_ascii=False, indent=2).encode("utf-8")
        filename = f"{novel.title}.json"
        media_type = "application/json"
    else:
        lines = [f"{novel.title}\n作者: {novel.author}\n{'=' * 40}\n\n"]
        for ch in chapters:
            content = _decompress_content(ch.content) if ch.content else ""
            lines.append(f"第{ch.chapter_index}章 {ch.title}\n\n{content}\n\n{'─' * 40}\n\n")
        content_bytes = "".join(lines).encode("utf-8")
        filename = f"{novel.title}.txt"
        media_type = "text/plain; charset=utf-8"

    stream = io.BytesIO(content_bytes)
    return StreamingResponse(
        stream,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{filename}"},
    )


@router.post("/import", response_model=BatchImportResponse)
async def batch_import(
    data: ImportReq,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = BatchImportResponse()

    if data.source == "local" and data.path:
        books_path = Path(data.path)
        if not books_path.exists():
            raise HTTPException(status_code=400, detail="指定路径不存在")

        for novel_dir in sorted(books_path.iterdir()):
            if not novel_dir.is_dir():
                continue
            try:
                loaded = await load_novel_from_dir(db, novel_dir)
                if loaded:
                    result.imported_count += 1
                else:
                    result.skipped_count += 1
            except Exception as e:
                result.errors.append(f"{novel_dir.name}: {str(e)}")

        await delete_cached_pattern("novel:*")
        await db.commit()
    else:
        raise HTTPException(status_code=400, detail="暂不支持该导入方式")

    return result
