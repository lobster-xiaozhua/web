import uuid
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel
from app.models.chapter import Chapter


class TestAuthRequiredEndpoints:
    @pytest.mark.asyncio
    async def test_reading_progress_requires_auth(self, client: AsyncClient):
        fake_novel_id = str(uuid.uuid4())
        response = await client.get(f"/api/novels/{fake_novel_id}/progress")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_progress_requires_auth(self, client: AsyncClient):
        fake_novel_id = str(uuid.uuid4())
        response = await client.post(
            f"/api/novels/{fake_novel_id}/progress",
            json={"chapter_id": str(uuid.uuid4()), "progress_percent": 50.0},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_bookmarks_list_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/bookmarks")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_bookmarks_create_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/bookmarks",
            json={"novel_id": str(uuid.uuid4())},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_bookmarks_delete_requires_auth(self, client: AsyncClient):
        response = await client.delete(f"/api/bookmarks/{uuid.uuid4()}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_bookmarks_stats_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/bookmarks/stats")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_export_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/export/novel",
            json={"novel_id": str(uuid.uuid4())},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_import_requires_auth(self, client: AsyncClient):
        response = await client.post(
            "/api/export/import",
            json={"source": "local", "path": "/some/path"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_system_config_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/system/config")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_crawler_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/crawler/sources")
        assert response.status_code == 401


class TestInvalidAuthHeaders:
    @pytest.mark.asyncio
    async def test_invalid_bearer_token(self, client: AsyncClient):
        headers = {"Authorization": "Bearer invalid-token-123"}
        response = await client.get("/api/bookmarks", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_malformed_auth_header(self, client: AsyncClient):
        headers = {"Authorization": "NotBearer token123"}
        response = await client.get("/api/bookmarks", headers=headers)
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_empty_bearer_token(self, client: AsyncClient):
        headers = {"Authorization": "Bearer "}
        response = await client.get("/api/bookmarks", headers=headers)
        assert response.status_code == 401


class TestAuthenticatedAccessControl:
    @pytest.mark.asyncio
    async def test_cannot_modify_other_user_progress(self, client: AsyncClient, db: AsyncSession):
        novel = Novel(title="进度隔离测试", author="测试作者")
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

        other_reg = await client.post(
            "/api/auth/register",
            json={
                "username": "otherprogress",
                "email": "otherprogress@example.com",
                "password": "pass123456",
            },
        )
        other_login = await client.post(
            "/api/auth/login",
            json={"username": "otherprogress", "password": "pass123456"},
        )
        other_token = other_login.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}

        await client.post(
            f"/api/novels/{novel.id}/progress",
            json={
                "chapter_id": str(chapter.id),
                "progress_percent": 50.0,
            },
            headers=other_headers,
        )

        new_reg = await client.post(
            "/api/auth/register",
            json={
                "username": "newprogress",
                "email": "newprogress@example.com",
                "password": "pass123456",
            },
        )
        new_login = await client.post(
            "/api/auth/login",
            json={"username": "newprogress", "password": "pass123456"},
        )
        new_token = new_login.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}

        response = await client.get(
            f"/api/novels/{novel.id}/progress",
            headers=new_headers,
        )
        assert response.status_code == 404
