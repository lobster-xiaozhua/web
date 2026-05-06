import os
import secrets
import logging
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = ""
    DATABASE_TYPE: str = "auto"
    REDIS_URL: str = "redis://localhost:6379/0"
    ES_URL: str = "http://localhost:9200"
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    BOOKS_DIR: str = os.path.join(os.getcwd(), "books")
    CRAWLER_GRPC_ADDR: str = "localhost:50051"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80", "http://localhost:3001"]
    LOG_LEVEL: str = "INFO"
    ENABLE_RATE_LIMIT: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    CACHE_TTL: int = 300
    SEARCH_FALLBACK: bool = True
    DATA_DIR: str = os.path.join(os.getcwd(), "data")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}

    def resolve_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL

        if self.DATABASE_TYPE == "sqlite":
            return self._sqlite_url()

        if self.DATABASE_TYPE == "postgres":
            return "postgresql+asyncpg://postgres:postgres@localhost:5432/novel_db"

        try:
            import asyncpg
            return "postgresql+asyncpg://postgres:postgres@localhost:5432/novel_db"
        except ImportError:
            pass

        return self._sqlite_url()

    def _sqlite_url(self) -> str:
        db_path = os.path.join(self.DATA_DIR, "novel.db")
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return f"sqlite+aiosqlite:///{db_path}"

    def is_sqlite(self) -> bool:
        return self.resolve_database_url().startswith("sqlite")


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    if not settings.SECRET_KEY:
        if os.environ.get("ENVIRONMENT") == "production":
            raise ValueError(
                "生产环境必须设置 SECRET_KEY 环境变量，请设置一个至少32字节的随机字符串"
            )
        settings.SECRET_KEY = secrets.token_urlsafe(32)
        logging.warning(
            "未设置 SECRET_KEY，已自动生成临时密钥。请在生产环境中通过环境变量设置安全的密钥！"
        )
    return settings
