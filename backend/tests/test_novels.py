import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel


@pytest.mark.asyncio
async def test_list_novels_empty(client: AsyncClient):
    response = await client.get("/api/novels")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["items"] == []


@pytest.mark.asyncio
async def test_list_novels_with_data(client: AsyncClient, db: AsyncSession):
    novel = Novel(
        title="测试小说",
        author="测试作者",
        category="玄幻",
    )
    db.add(novel)
    await db.commit()

    response = await client.get("/api/novels")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_novel_not_found(client: AsyncClient):
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/api/novels/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_categories(client: AsyncClient):
    response = await client.get("/api/novels/categories")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_recommended(client: AsyncClient):
    response = await client.get("/api/novels/recommended")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_list_novels_with_category_filter(client: AsyncClient, db: AsyncSession):
    novel = Novel(
        title="分类测试小说",
        author="测试作者",
        category="科幻",
    )
    db.add(novel)
    await db.commit()

    response = await client.get("/api/novels?category=科幻")
    assert response.status_code == 200
