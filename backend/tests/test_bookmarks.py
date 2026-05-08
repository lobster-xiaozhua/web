import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.advanced import Bookmark, ReadingStats


@pytest.mark.asyncio
async def test_list_bookmarks(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/bookmarks", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    from app.models.novel import Novel

    novel = Novel(title="收藏测试小说", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id)},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["novel_id"] == str(novel.id)


@pytest.mark.asyncio
async def test_create_duplicate_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    from app.models.novel import Novel

    novel = Novel(title="重复收藏测试", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id)},
        headers=auth_headers,
    )

    response = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id), "note": "再次收藏"},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "已收藏" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_bookmark_nonexistent_novel(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert "不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    from app.models.novel import Novel

    novel = Novel(title="删除书签测试", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    create_resp = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id), "note": "测试书签"},
        headers=auth_headers,
    )
    bookmark_id = create_resp.json()["id"]

    delete_resp = await client.delete(
        f"/api/bookmarks/{bookmark_id}",
        headers=auth_headers,
    )
    assert delete_resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_nonexistent_bookmark(client: AsyncClient, auth_headers: dict):
    response = await client.delete(
        f"/api/bookmarks/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_check_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    from app.models.novel import Novel

    novel = Novel(title="检查书签测试", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id)},
        headers=auth_headers,
    )

    response = await client.get(
        f"/api/bookmarks/check/{novel.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bookmarked"] is True


@pytest.mark.asyncio
async def test_check_bookmark_not_bookmarked(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    from app.models.novel import Novel

    novel = Novel(title="未收藏小说", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.get(
        f"/api/bookmarks/check/{novel.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["bookmarked"] is False


@pytest.mark.asyncio
async def test_get_reading_stats(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    response = await client.get(
        "/api/bookmarks/stats",
        headers=auth_headers,
        params={"days": 7},
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_chapters" in data
    assert "total_words" in data
    assert "total_minutes" in data
    assert "streak_days" in data


@pytest.mark.asyncio
async def test_get_reading_stats_invalid_days(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/bookmarks/stats",
        headers=auth_headers,
        params={"days": 500},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_bookmark_requires_auth(client: AsyncClient):
    response = await client.get("/api/bookmarks")
    assert response.status_code == 401
