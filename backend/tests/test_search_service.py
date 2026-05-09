import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestSearchService:
    @pytest.mark.asyncio
    async def test_get_es_client_unavailable(self):
        from app.services.search_service import get_es_client
        with patch("app.services.search_service._es_available", False):
            client = await get_es_client()
            assert client is None

    @pytest.mark.asyncio
    async def test_get_es_client_available(self):
        from app.services.search_service import get_es_client
        mock_client = MagicMock()
        with patch("app.services.search_service._es_available", True):
            with patch("app.services.search_service.es_client", mock_client):
                client = await get_es_client()
                assert client == mock_client


class TestESSearch:
    @pytest.mark.asyncio
    async def test_es_search_handles_errors(self):
        from app.services.search_service import _es_search
        mock_client = AsyncMock()
        mock_client.search = AsyncMock(side_effect=Exception("ES error"))

        with pytest.raises(Exception):
            await _es_search(mock_client, "test", 10)
