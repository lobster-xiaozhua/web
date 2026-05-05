import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.novel import NovelStatus


class NovelCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(default="未知", max_length=100)
    cover_url: Optional[str] = None
    category: str = Field(default="未分类", max_length=50)
    status: NovelStatus = NovelStatus.ongoing
    total_words: int = 0
    description: Optional[str] = None
    source_id: Optional[str] = None
    source_novel_id: Optional[str] = None


class NovelResponse(BaseModel):
    id: uuid.UUID
    title: str
    author: str
    cover_url: Optional[str] = None
    category: str
    status: NovelStatus
    total_words: int
    description: Optional[str] = None
    rating: float
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class NovelListResponse(BaseModel):
    total: int
    items: list[NovelResponse]
    page: int
    page_size: int


class ChapterBrief(BaseModel):
    id: uuid.UUID
    title: str
    chapter_index: int
    word_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class NovelDetailResponse(NovelResponse):
    chapters: list[ChapterBrief] = []
