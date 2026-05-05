import uuid
from datetime import datetime, timezone

from sqlalchemy import String, Integer, LargeBinary, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.user import Base


class Chapter(Base):
    __tablename__ = "chapters"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_chapter_content_hash"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    novel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    chapter_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    simhash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)


class ArchivedChapter(Base):
    __tablename__ = "archived_chapters"
    __table_args__ = (
        UniqueConstraint("content_hash", name="uq_archived_chapter_content_hash"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    novel_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    chapter_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    simhash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    word_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
