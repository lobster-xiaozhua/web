import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import make_asgi_app

from app.api.auth import router as auth_router
from app.api.novels import router as novels_router
from app.api.chapters import router as chapters_router
from app.api.search import router as search_router
from app.api.crawler import router as crawler_router
from app.core.config import get_settings
from app.db.database import engine
from app.models.user import Base
from app.services.cache import close_redis
from app.services.search_service import close_es, ensure_index
from app.services.book_loader import scan_books_dir, start_watching
from app.services.crawler_client import crawler_client

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("应用启动中...")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表已创建")

    try:
        await ensure_index()
        logger.info("Elasticsearch索引已就绪")
    except Exception as e:
        logger.warning("Elasticsearch连接失败: %s", e)

    try:
        await crawler_client.connect()
    except Exception as e:
        logger.warning("gRPC爬虫客户端连接失败: %s", e)

    try:
        await scan_books_dir()
    except Exception as e:
        logger.warning("扫描books目录失败: %s", e)

    observer = start_watching()

    logger.info("应用启动完成")
    yield

    logger.info("应用关闭中...")
    observer.stop()
    observer.join(timeout=5)

    await close_redis()
    await close_es()
    await crawler_client.close()
    await engine.dispose()
    logger.info("应用已关闭")


app = FastAPI(
    title="小说阅读平台后端",
    description="提供用户认证、小说/章节API、搜索、爬虫协调等功能",
    version="1.0.0",
    lifespan=lifespan,
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(novels_router)
app.include_router(chapters_router)
app.include_router(search_router)
app.include_router(crawler_router)

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
