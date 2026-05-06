from pydantic_settings import BaseSettings
from functools import lru_cache
import secrets
import logging

_INSECURE_DEFAULT_KEY = "super-secret-key-change-in-production"


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/novel_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    ES_URL: str = "http://localhost:9200"
    SECRET_KEY: str = _INSECURE_DEFAULT_KEY
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    BOOKS_DIR: str = "/app/books"
    CRAWLER_GRPC_ADDR: str = "localhost:50051"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    settings = Settings()
    if settings.SECRET_KEY == _INSECURE_DEFAULT_KEY:
        logging.warning(
            "使用默认 SECRET_KEY，请在生产环境中通过环境变量设置安全的密钥！"
        )
    return settings
