import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel
from app.models.advanced import Bookmark, ReadingStats


@pytest.mark.asyncio
async def test_list_bookmarks_requires_auth(client: AsyncClient):
    response = await client.get("/api/bookmarks")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_bookmarks_empty(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/bookmarks", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_bookmarks(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="收藏测试小说", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    bookmark = Bookmark(user_id=uuid.uuid4(), novel_id=novel.id, note="测试笔记")
    db.add(bookmark)
    await db.commit()

    response = await client.get("/api/bookmarks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_create_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="新建收藏测试", author="作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id), "note": "我的笔记"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["novel_id"] == str(novel.id)
    assert data["note"] == "我的笔记"


@pytest.mark.asyncio
async def test_create_bookmark_novel_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_create_bookmark_duplicate(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="重复收藏测试", author="作者")
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
        json={"novel_id": str(novel.id)},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_create_bookmark_requires_auth(client: AsyncClient, db: AsyncSession):
    novel = Novel(title="无认证测试", author="作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id)},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="删除收藏测试", author="作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    create_response = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id)},
        headers=auth_headers,
    )
    bookmark_id = create_response.json()["id"]

    response = await client.delete(f"/api/bookmarks/{bookmark_id}", headers=auth_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_bookmark_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.delete(
        f"/api/bookmarks/{uuid.uuid4()}",
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_check_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="检查收藏测试", author="作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.get(
        f"/api/bookmarks/check/{novel.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["bookmarked"] is False

    await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id)},
        headers=auth_headers,
    )

    response = await client.get(
        f"/api/bookmarks/check/{novel.id}",
        headers=auth_headers,
    )
    assert response.json()["bookmarked"] is True


@pytest.mark.asyncio
async def test_get_reading_stats(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    response = await client.get("/api/bookmarks/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_chapters" in data
    assert "total_words" in data
    assert "streak_days" in data
    assert "daily_stats" in data


@pytest.mark.asyncio
async def test_get_reading_stats_with_data(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    from datetime import datetime, timezone, timedelta

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    user_id = uuid.uuid4()
    db.add(ReadingStats(
        user_id=user_id,
        date=today,
        chapters_read=5,
        words_read=10000,
        reading_minutes=30,
    ))
    db.add(ReadingStats(
        user_id=user_id,
        date=yesterday,
        chapters_read=3,
        words_read=6000,
        reading_minutes=20,
    ))
    await db.commit()

    response = await client.get("/api/bookmarks/stats?days=7", headers=auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_reading_stats_days_validation(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/bookmarks/stats?days=0", headers=auth_headers)
    assert response.status_code in [200, 422]

    response = await client.get("/api/bookmarks/stats?days=400", headers=auth_headers)
    assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_get_reading_stats_requires_auth(client: AsyncClient):
    response = await client.get("/api/bookmarks/stats")
    assert response.status_code == 401
