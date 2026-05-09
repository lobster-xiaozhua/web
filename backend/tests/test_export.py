import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel
from app.models.chapter import Chapter


@pytest.mark.asyncio
async def test_export_novel_not_found(client: AsyncClient, auth_headers: dict):
    fake_id = str(uuid.uuid4())
    response = await client.post(
        "/api/export/novel",
        json={"novel_id": fake_id},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert "小说不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_export_novel_unauthorized(client: AsyncClient, db: AsyncSession):
    novel = Novel(title="未授权导出", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id)},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_invalid_chapter_range(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="无效范围测试", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "chapter_range": "invalid"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "章节范围格式错误" in response.json()["detail"]


@pytest.mark.asyncio
async def test_batch_import_invalid_path(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/export/import",
        json={"source": "local", "path": "/nonexistent/path"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "路径不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_batch_import_unsupported_source(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/export/import",
        json={"source": "url", "urls": ["http://example.com"]},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "暂不支持" in response.json()["detail"]
