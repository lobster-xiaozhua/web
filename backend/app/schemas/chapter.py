import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ChapterResponse(BaseModel):
    id: uuid.UUID
    novel_id: uuid.UUID
    title: str
    chapter_index: int
    word_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ChapterContentResponse(BaseModel):
    id: uuid.UUID
    novel_id: uuid.UUID
    title: str
    chapter_index: int
    content: str
    word_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ReadingProgressCreate(BaseModel):
    chapter_id: uuid.UUID
    progress_percent: float = Field(..., ge=0.0, le=100.0)


class ReadingProgressResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    novel_id: uuid.UUID
    chapter_id: Optional[uuid.UUID] = None
    progress_percent: float
    last_read_at: datetime

    model_config = {"from_attributes": True}
