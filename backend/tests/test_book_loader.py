import pytest
from pathlib import Path
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.book_loader import (
    parse_chapter_filename,
    _compress_content,
    _decompress_content,
    _compute_content_hash,
)


def test_parse_chapter_filename_standard():
    result = parse_chapter_filename("第001章_标题.txt")
    assert result is not None
    assert result[0] == 1
    assert result[1] == "标题"


def test_parse_chapter_filename_with_space():
    result = parse_chapter_filename("第100章 另一个标题.txt")
    assert result is not None
    assert result[0] == 100
    assert result[1] == "另一个标题"


def test_parse_chapter_filename_invalid():
    result = parse_chapter_filename("invalid_file.txt")
    assert result is None


def test_parse_chapter_filename_no_extension():
    result = parse_chapter_filename("第001章_标题.csv")
    assert result is None


def test_compress_and_decompress():
    text = "这是一段测试文本，用于验证压缩和解压缩功能。" * 100
    compressed = _compress_content(text)
    assert isinstance(compressed, bytes)
    assert len(compressed) < len(text.encode("utf-8"))

    decompressed = _decompress_content(compressed)
    assert decompressed == text


def test_compute_content_hash():
    text = "测试内容"
    hash1 = _compute_content_hash(text)
    hash2 = _compute_content_hash(text)
    assert hash1 == hash2
    assert len(hash1) == 64

    different_text = "不同内容"
    hash3 = _compute_content_hash(different_text)
    assert hash1 != hash3


@pytest.mark.asyncio
async def test_load_chapter_from_file(tmp_path):
    from app.services.book_loader import load_chapter_from_file

    chapter_file = tmp_path / "第001章_测试标题.txt"
    chapter_file.write_text("这是章节内容", encoding="utf-8")

    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.flush = AsyncMock()

    novel_id = MagicMock()

    chapter = await load_chapter_from_file(mock_session, novel_id, chapter_file)
    assert chapter is not None
    assert chapter.chapter_index == 1
    assert chapter.title == "测试标题"
    assert chapter.word_count > 0


@pytest.mark.asyncio
async def test_load_chapter_from_file_invalid_name(tmp_path):
    from app.services.book_loader import load_chapter_from_file

    invalid_file = tmp_path / "invalid.txt"
    invalid_file.write_text("内容", encoding="utf-8")

    mock_session = AsyncMock()
    novel_id = MagicMock()

    chapter = await load_chapter_from_file(mock_session, novel_id, invalid_file)
    assert chapter is None
