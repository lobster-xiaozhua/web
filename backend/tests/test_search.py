import pytest
from unittest.mock import AsyncMock, patch
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_search_endpoint(client: AsyncClient):
    mock_results = [
        {
            "id": "test-id",
            "score": 10.5,
            "source": {"title": "测试小说", "author": "测试作者"},
            "highlight": {},
        }
    ]

    with patch("app.api.search.search_novels", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_results
        response = await client.get("/api/search?q=测试")

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "测试"
    assert len(data["results"]) == 1


@pytest.mark.asyncio
async def test_search_missing_query(client: AsyncClient):
    response = await client.get("/api/search")
    assert response.status_code == 422
