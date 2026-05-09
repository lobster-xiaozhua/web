import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel
from app.models.advanced import Bookmark


@pytest.mark.asyncio
async def test_list_bookmarks_empty(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/bookmarks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_list_bookmarks_unauthorized(client: AsyncClient):
    response = await client.get("/api/bookmarks")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="书签测试小说", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id), "note": "我的书签"},
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["novel_id"] == str(novel.id)
    assert data["note"] == "我的书签"


@pytest.mark.asyncio
async def test_create_bookmark_novel_not_found(client: AsyncClient, auth_headers: dict):
    fake_id = str(uuid.uuid4())
    response = await client.post(
        "/api/bookmarks",
        json={"novel_id": fake_id},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert "小说不存在" in response.json()["detail"]


@pytest.mark.asyncio
async def test_create_duplicate_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="重复书签测试", author="测试作者")
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
    assert "已收藏" in response.json()["detail"]


@pytest.mark.asyncio
async def test_delete_bookmark(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="删除书签测试", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    create_resp = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id)},
        headers=auth_headers,
    )
    bookmark_id = create_resp.json()["id"]

    response = await client.delete(f"/api/bookmarks/{bookmark_id}", headers=auth_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_bookmark_not_found(client: AsyncClient, auth_headers: dict):
    fake_id = str(uuid.uuid4())
    response = await client.delete(f"/api/bookmarks/{fake_id}", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_bookmark_other_user(client: AsyncClient, db: AsyncSession):
    novel = Novel(title="跨用户书签测试", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    other_reg = await client.post(
        "/api/auth/register",
        json={
            "username": "otherbookmark",
            "email": "otherbookmark@example.com",
            "password": "pass123456",
        },
    )
    other_login = await client.post(
        "/api/auth/login",
        json={"username": "otherbookmark", "password": "pass123456"},
    )
    other_token = other_login.json()["access_token"]
    other_headers = {"Authorization": f"Bearer {other_token}"}

    bookmark_resp = await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id)},
        headers=other_headers,
    )
    bookmark_id = bookmark_resp.json()["id"]

    current_reg = await client.post(
        "/api/auth/register",
        json={
            "username": "currentbookmark",
            "email": "currentbookmark@example.com",
            "password": "pass123456",
        },
    )
    current_login = await client.post(
        "/api/auth/login",
        json={"username": "currentbookmark", "password": "pass123456"},
    )
    current_token = current_login.json()["access_token"]
    current_headers = {"Authorization": f"Bearer {current_token}"}

    response = await client.delete(f"/api/bookmarks/{bookmark_id}", headers=current_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_check_bookmark_exists(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="检查书签测试", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    await client.post(
        "/api/bookmarks",
        json={"novel_id": str(novel.id)},
        headers=auth_headers,
    )

    response = await client.get(f"/api/bookmarks/check/{novel.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["bookmarked"] is True


@pytest.mark.asyncio
async def test_check_bookmark_not_exists(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="未收藏小说", author="测试作者")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.get(f"/api/bookmarks/check/{novel.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["bookmarked"] is False


@pytest.mark.asyncio
async def test_get_reading_stats_empty(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/bookmarks/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_chapters"] == 0
    assert data["total_words"] == 0
    assert data["total_minutes"] == 0
    assert data["streak_days"] == 0


@pytest.mark.asyncio
async def test_get_reading_stats_with_data(client: AsyncClient, db: AsyncSession):
    from datetime import datetime, timedelta, timezone
    from app.models.advanced import ReadingStats
    from app.models.user import User
    from app.core.security import get_password_hash

    unique_id = uuid.uuid4().hex[:8]
    user = User(
        username=f"statstest_{unique_id}",
        email=f"statstest_{unique_id}@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
    )
    db.add(user)
    await db.flush()

    today = datetime.now(timezone.utc)
    for i in range(3):
        stat = ReadingStats(
            user_id=user.id,
            date=(today - timedelta(days=i)).strftime("%Y-%m-%d"),
            chapters_read=5,
            words_read=10000,
            reading_minutes=30,
        )
        db.add(stat)
    await db.commit()

    login = await client.post(
        "/api/auth/login",
        json={
            "username": f"statstest_{unique_id}",
            "password": "password123",
        },
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/bookmarks/stats?days=7", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_chapters"] == 15
    assert data["total_words"] == 30000
    assert data["total_minutes"] == 90
