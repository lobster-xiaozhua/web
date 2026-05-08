import uuid
import pytest
import json
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel
from app.models.chapter import Chapter


@pytest.mark.asyncio
async def test_export_novel_as_json(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="导出测试小说", author="测试作者", category="科幻")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    chapter = Chapter(
        novel_id=novel.id,
        title="第一章 测试",
        chapter_index=1,
        word_count=100,
        content=None,
    )
    db.add(chapter)
    await db.commit()

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "format": "json"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

    data = response.json()
    assert data["title"] == "导出测试小说"
    assert data["author"] == "测试作者"
    assert len(data["chapters"]) >= 1


@pytest.mark.asyncio
async def test_export_novel_as_txt(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="TXT导出小说", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "format": "txt"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_novel_with_chapter_range(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="范围导出测试", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    for i in range(1, 6):
        chapter = Chapter(
            novel_id=novel.id,
            title=f"第{i}章",
            chapter_index=i,
            word_count=100,
        )
        db.add(chapter)
    await db.commit()

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "format": "json", "chapter_range": "2-4"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["chapters"]) == 3


@pytest.mark.asyncio
async def test_export_novel_invalid_range(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="无效范围测试", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "format": "json", "chapter_range": "invalid"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "格式错误" in response.json()["detail"]


@pytest.mark.asyncio
async def test_export_nonexistent_novel(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(uuid.uuid4()), "format": "json"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_requires_auth(client: AsyncClient):
    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(uuid.uuid4())},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_batch_import_local_path_not_exists(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/export/import",
        json={"source": "local", "path": "/nonexistent/path"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_batch_import_unsupported_source(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/export/import",
        json={"source": "remote", "url": "http://example.com"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "暂不支持" in response.json()["detail"]
