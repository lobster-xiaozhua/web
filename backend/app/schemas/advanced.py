import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class BookmarkCreate(BaseModel):
    novel_id: uuid.UUID
    note: Optional[str] = None


class BookmarkResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    novel_id: uuid.UUID
    note: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReadingStatsResponse(BaseModel):
    date: str
    chapters_read: int
    words_read: int
    reading_minutes: int

    model_config = {"from_attributes": True}


class ReadingStatsSummary(BaseModel):
    total_chapters: int = 0
    total_words: int = 0
    total_minutes: int = 0
    streak_days: int = 0
    daily_stats: list[ReadingStatsResponse] = []


class ExportRequest(BaseModel):
    novel_id: uuid.UUID
    format: str = Field(default="txt", pattern="^(txt|json)$")
    chapter_range: Optional[str] = None


class BatchImportRequest(BaseModel):
    source: str = Field(default="local", pattern="^(local|url)$")
    path: Optional[str] = None
    urls: Optional[list[str]] = None


class BatchImportResponse(BaseModel):
    imported_count: int = 0
    skipped_count: int = 0
    errors: list[str] = []


class SystemConfigCreate(BaseModel):
    key: str = Field(..., min_length=1, max_length=100)
    value: str
    description: Optional[str] = None


class SystemConfigResponse(BaseModel):
    id: uuid.UUID
    key: str
    value: str
    description: Optional[str] = None
    updated_at: datetime

    model_config = {"from_attributes": True}


class SystemStatusResponse(BaseModel):
    version: str
    database: str
    redis: str
    elasticsearch: str
    crawler: str
    books_count: int
    uptime_seconds: float
