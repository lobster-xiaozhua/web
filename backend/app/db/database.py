import logging
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import event
from typing import AsyncGenerator

from app.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()
resolved_url = settings.resolve_database_url()

engine_kwargs = {
    "echo": False,
}

if settings.is_sqlite():
    engine_kwargs["pool_size"] = 1
    engine_kwargs["max_overflow"] = 0
    engine_kwargs["connect_args"] = {"check_same_thread": False}
    logger.info("使用 SQLite 数据库: %s", resolved_url)
else:
    engine_kwargs["pool_size"] = settings.DB_POOL_SIZE
    engine_kwargs["max_overflow"] = settings.DB_MAX_OVERFLOW
    logger.info("使用 PostgreSQL 数据库: %s", resolved_url.split("@")[-1] if "@" in resolved_url else resolved_url)

engine = create_async_engine(resolved_url, **engine_kwargs)


if settings.is_sqlite():
    @event.listens_for(engine.sync_engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.close()


async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
