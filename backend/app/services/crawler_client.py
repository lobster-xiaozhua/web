import asyncio
import logging
from typing import Optional

import grpc

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class CrawlerClient:
    def __init__(self):
        self.channel: Optional[grpc.aio.Channel] = None

    async def connect(self):
        settings = get_settings()
        self.channel = grpc.aio.insecure_channel(settings.CRAWLER_GRPC_ADDR)
        try:
            await asyncio.wait_for(
                self.channel.channel_ready(),
                timeout=5,
            )
            logger.info("gRPC连接已建立: %s", settings.CRAWLER_GRPC_ADDR)
        except asyncio.TimeoutError:
            logger.warning("gRPC连接超时: %s", settings.CRAWLER_GRPC_ADDR)
        except Exception as e:
            logger.warning("gRPC连接失败: %s", e)

    async def close(self):
        if self.channel:
            await self.channel.close()
            self.channel = None

    async def _ensure_connected(self):
        if not self.channel:
            await self.connect()

    async def start_crawl(self, source_id: str, novel_url: str) -> dict:
        await self._ensure_connected()
        try:
            method = self.channel.unary_unary(
                "/crawler.CrawlerService/StartCrawl",
                request_serializer=lambda x: x,
                response_deserializer=lambda x: x,
            )
            response = await method(
                b"",
                metadata=[
                    ("source_id", source_id),
                    ("novel_url", novel_url),
                ],
            )
            return {"status": "started", "detail": str(response)}
        except grpc.aio.AioRpcError as e:
            logger.error("启动爬虫失败: %s", e)
            return {"status": "error", "detail": str(e)}

    async def get_status(self, source_id: str) -> dict:
        await self._ensure_connected()
        try:
            method = self.channel.unary_unary(
                "/crawler.CrawlerService/GetStatus",
                request_serializer=lambda x: x,
                response_deserializer=lambda x: x,
            )
            response = await method(
                b"",
                metadata=[("source_id", source_id)],
            )
            return {"status": "ok", "detail": str(response)}
        except grpc.aio.AioRpcError as e:
            logger.error("获取爬虫状态失败: %s", e)
            return {"status": "error", "detail": str(e)}

    async def list_sources(self) -> list[dict]:
        await self._ensure_connected()
        try:
            method = self.channel.unary_unary(
                "/crawler.CrawlerService/ListSources",
                request_serializer=lambda x: x,
                response_deserializer=lambda x: x,
            )
            response = await method(b"")
            return [{"id": "default", "name": "默认书源", "detail": str(response)}]
        except grpc.aio.AioRpcError as e:
            logger.error("获取书源列表失败: %s", e)
            return []


crawler_client = CrawlerClient()
