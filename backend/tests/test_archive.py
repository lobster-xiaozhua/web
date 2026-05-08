import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

from app.services.archive import archive_old_novels
from app.models.novel import Novel, NovelStatus


@pytest.mark.asyncio
async def test_archive_old_novels_no_matches():
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    count = await archive_old_novels(mock_session)
    assert count == 0


@pytest.mark.asyncio
async def test_archive_old_novels_with_novels():
    mock_session = MagicMock()

    old_novel = MagicMock()
    old_novel.id = "novel-1"
    old_novel.title = "旧小说"

    chapters = [
        MagicMock(id=f"ch-{i}", title=f"第{i}章", novel_id="novel-1")
        for i in range(1, 4)
    ]

    mock_novel_result = MagicMock()
    mock_novel_result.scalars.return_value.all.return_value = [old_novel]
    mock_chapters_result = MagicMock()
    mock_chapters_result.scalars.return_value.all.return_value = chapters

    mock_session.execute = AsyncMock(side_effect=[mock_novel_result, mock_chapters_result])
    mock_session.add_all = MagicMock()
    mock_session.execute = AsyncMock()
    mock_session.flush = AsyncMock()

    from app.models.chapter import Chapter, ArchivedChapter

    original_add_all = mock_session.add_all
    added_archived_chapters = []

    def capture_add_all(items):
        added_archived_chapters.extend(items)
        return original_add_all(items)

    mock_session.add_all = MagicMock(side_effect=capture_add_all)

    mock_novel_result.scalars.return_value.all.side_effect = [
        [old_novel],
        chapters
    ]

    count = await archive_old_novels(mock_session)
    assert count == 3


@pytest.mark.asyncio
async def test_archive_old_novels_empty_novel_list():
    mock_session = MagicMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_result)

    count = await archive_old_novels(mock_session)
    assert count == 0
