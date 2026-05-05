import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import String, Enum, Integer, Float, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base


class NovelStatus(str, enum.Enum):
    ongoing = "ongoing"
    completed = "completed"
    hiatus = "hiatus"


class Novel(Base):
    __tablename__ = "novels"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False, default="未知")
    cover_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="未分类")
    status: Mapped[NovelStatus] = mapped_column(Enum(NovelStatus), default=NovelStatus.ongoing, nullable=False)
    total_words: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_novel_id: Mapped[str | None] = mapped_column(String(200), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
