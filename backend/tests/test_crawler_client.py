import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.crawler_client import CrawlerClient, crawler_client


class TestCrawlerClient:
    def test_client_initialization(self):
        client = CrawlerClient()
        assert client.channel is None

    @pytest.mark.asyncio
    async def test_start_crawl_without_grpc(self):
        client = CrawlerClient()

        with patch("app.services.crawler_client._grpc_available", False):
            result = await client.start_crawl("source1", "http://example.com")
            assert result["status"] == "error"
            assert "不可用" in result["detail"]

    @pytest.mark.asyncio
    async def test_get_status_without_grpc(self):
        client = CrawlerClient()

        with patch("app.services.crawler_client._grpc_available", False):
            result = await client.get_status("source1")
            assert result["status"] == "error"
            assert "不可用" in result["detail"]

    @pytest.mark.asyncio
    async def test_list_sources_without_grpc(self):
        client = CrawlerClient()

        with patch("app.services.crawler_client._grpc_available", False):
            result = await client.list_sources()
            assert result == []


@pytest.mark.asyncio
async def test_crawler_client_connect_without_grpc():
    client = CrawlerClient()

    with patch("app.services.crawler_client._grpc_available", False):
        await client.connect()


@pytest.mark.asyncio
async def test_crawler_client_close_without_channel():
    client = CrawlerClient()
    await client.close()
    assert client.channel is None
