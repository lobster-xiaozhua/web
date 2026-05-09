import pytest
from httpx import AsyncClient


class TestUserRegistrationValidation:
    @pytest.mark.asyncio
    async def test_register_short_username(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "ab",
                "email": "valid@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_long_username(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "a" * 51,
                "email": "valid@example.com",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_invalid_email(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "validuser",
                "email": "not-an-email",
                "password": "password123",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_short_password(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "validuser",
                "email": "valid@example.com",
                "password": "12345",
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_long_password(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "validuser",
                "email": "valid@example.com",
                "password": "a" * 129,
            },
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_missing_fields(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={"username": "testuser"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_register_empty_body(self, client: AsyncClient):
        response = await client.post(
            "/api/auth/register",
            json={},
        )
        assert response.status_code == 422


class TestSearchValidation:
    @pytest.mark.asyncio
    async def test_search_empty_query(self, client: AsyncClient):
        response = await client.get("/api/search?q=")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_missing_query(self, client: AsyncClient):
        response = await client.get("/api/search")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_query_too_long(self, client: AsyncClient):
        long_query = "a" * 201
        response = await client.get(f"/api/search?q={long_query}")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_search_size_limit(self, client: AsyncClient):
        response = await client.get("/api/search?q=test&size=150")
        assert response.status_code == 422


class TestNovelsValidation:
    @pytest.mark.asyncio
    async def test_list_novels_invalid_page(self, client: AsyncClient):
        response = await client.get("/api/novels?page=0")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_novels_negative_page(self, client: AsyncClient):
        response = await client.get("/api/novels?page=-1")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_novels_page_size_too_large(self, client: AsyncClient):
        response = await client.get("/api/novels?page_size=150")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_list_novels_invalid_uuid(self, client: AsyncClient):
        response = await client.get("/api/novels/not-a-uuid")
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_recommended_limit(self, client: AsyncClient):
        response = await client.get("/api/novels/recommended?limit=100")
        assert response.status_code == 422


class TestReadingProgressValidation:
    @pytest.mark.asyncio
    async def test_update_progress_invalid_chapter_id(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/novels/123e4567-e89b-12d3-a456-426614174000/progress",
            json={
                "chapter_id": "not-a-uuid",
                "progress_percent": 50.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_progress_negative_percent(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/novels/123e4567-e89b-12d3-a456-426614174000/progress",
            json={
                "chapter_id": "123e4567-e89b-12d3-a456-426614174000",
                "progress_percent": -10.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_progress_percent_over_100(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/novels/123e4567-e89b-12d3-a456-426614174000/progress",
            json={
                "chapter_id": "123e4567-e89b-12d3-a456-426614174000",
                "progress_percent": 150.0,
            },
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestBookmarkValidation:
    @pytest.mark.asyncio
    async def test_create_bookmark_invalid_uuid(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/bookmarks",
            json={"novel_id": "invalid-uuid"},
            headers=auth_headers,
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_create_bookmark_missing_novel_id(self, client: AsyncClient, auth_headers: dict):
        response = await client.post(
            "/api/bookmarks",
            json={},
            headers=auth_headers,
        )
        assert response.status_code == 422


class TestReadingStatsValidation:
    @pytest.mark.asyncio
    async def test_stats_days_too_short(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/bookmarks/stats?days=0", headers=auth_headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_stats_days_too_long(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/api/bookmarks/stats?days=500", headers=auth_headers)
        assert response.status_code == 422
