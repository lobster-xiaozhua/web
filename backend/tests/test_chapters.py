import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel
from app.models.chapter import Chapter


@pytest.mark.asyncio
async def test_get_chapter_not_found(client: AsyncClient):
    fake_novel_id = str(uuid.uuid4())
    response = await client.get(f"/api/novels/{fake_novel_id}/chapters/1")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_reading_progress_not_found(client: AsyncClient, auth_headers: dict):
    fake_novel_id = str(uuid.uuid4())
    response = await client.get(
        f"/api/novels/{fake_novel_id}/progress",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_reading_progress(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="进度测试小说", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    chapter = Chapter(
        novel_id=novel.id,
        title="第一章",
        chapter_index=1,
        word_count=1000,
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)

    response = await client.post(
        f"/api/novels/{novel.id}/progress",
        json={
            "chapter_id": str(chapter.id),
            "progress_percent": 50.0,
        },
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["progress_percent"] == 50.0


@pytest.mark.asyncio
async def test_get_reading_progress(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="进度查询测试小说", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    chapter = Chapter(
        novel_id=novel.id,
        title="第一章",
        chapter_index=1,
        word_count=1000,
    )
    db.add(chapter)
    await db.commit()
    await db.refresh(chapter)

    await client.post(
        f"/api/novels/{novel.id}/progress",
        json={
            "chapter_id": str(chapter.id),
            "progress_percent": 75.0,
        },
        headers=auth_headers,
    )

    response = await client.get(
        f"/api/novels/{novel.id}/progress",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["progress_percent"] == 75.0
