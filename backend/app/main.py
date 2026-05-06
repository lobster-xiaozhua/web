import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
try:
    from prometheus_client import make_asgi_app
    _prometheus_available = True
except ImportError:
    _prometheus_available = False

from app.api.auth import router as auth_router
from app.api.novels import router as novels_router
from app.api.chapters import router as chapters_router
from app.api.search import router as search_router
from app.api.crawler import router as crawler_router
from app.api.bookmarks import router as bookmarks_router
from app.api.export import router as export_router
from app.api.system import router as system_router
from app.core.config import get_settings
from app.core.middleware import ErrorHandlerMiddleware, RateLimitMiddleware, RequestLoggingMiddleware
from app.db.database import engine
from app.models.user import Base
from app.models.advanced import Bookmark, ReadingStats, SystemConfig
from app.services.cache import init_cache, close_redis
from app.services.search_service import init_search, close_es
from app.services.book_loader import scan_books_dir, start_watching
from app.services.crawler_client import crawler_client

logger = logging.getLogger(__name__)

_start_time = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    logger.info("星穹书阁 v1.5.0 启动中...")
    logger.info("数据库类型: %s", "SQLite" if settings.is_sqlite() else "PostgreSQL")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("数据库表已创建")

    await init_cache()

    await init_search()

    try:
        await crawler_client.connect()
    except Exception as e:
        logger.warning("gRPC爬虫客户端连接失败: %s", e)

    try:
        await scan_books_dir()
    except Exception as e:
        logger.warning("扫描books目录失败: %s", e)

    observer = start_watching()

    logger.info("星穹书阁 v1.5.0 启动完成")
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
    title="星穹书阁 - 小说阅读平台",
    description="提供用户认证、小说/章节API、搜索、爬虫协调、收藏、导出等功能",
    version="1.5.0",
    lifespan=lifespan,
)

settings = get_settings()

app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.RATE_LIMIT_PER_MINUTE)
app.add_middleware(RequestLoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["Content-Disposition"],
    max_age=600,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "detail": "请求参数验证失败",
            "errors": [
                {
                    "field": ".".join(str(loc) for loc in err["loc"]),
                    "message": err["msg"],
                }
                for err in exc.errors()
            ],
        },
    )


app.include_router(auth_router)
app.include_router(novels_router)
app.include_router(chapters_router)
app.include_router(search_router)
app.include_router(crawler_router)
app.include_router(bookmarks_router)
app.include_router(export_router)
app.include_router(system_router)

if _prometheus_available:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    from app.db.database import engine as eng
    from sqlalchemy import text

    db_status = "unknown"
    try:
        async with eng.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    return {
        "status": "ok" if db_status == "ok" else "degraded",
    }
