import uuid
import json
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.novel import Novel
from app.models.chapter import Chapter
from app.services.book_loader import _compress_content


@pytest.mark.asyncio
async def test_export_novel_requires_auth(client: AsyncClient):
    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(uuid.uuid4())},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_export_novel_not_found(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(uuid.uuid4())},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_export_novel_txt_format(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="TestNovel", author="TestAuthor", category="Fantasy")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    chapter = Chapter(
        novel_id=novel.id,
        title="Chapter 1",
        chapter_index=1,
        content=_compress_content("Chapter 1 content here."),
        word_count=20,
    )
    db.add(chapter)
    await db.commit()

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "format": "txt"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    content = response.text
    assert "TestNovel" in content
    assert "TestAuthor" in content


@pytest.mark.asyncio
async def test_export_novel_json_format(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="JSONExportTest", author="Author", category="SciFi")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    chapter = Chapter(
        novel_id=novel.id,
        title="Beginning",
        chapter_index=1,
        content=_compress_content("JSON format content test"),
        word_count=8,
    )
    db.add(chapter)
    await db.commit()

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "format": "json"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")

    data = response.json()
    assert data["title"] == "JSONExportTest"
    assert data["author"] == "Author"
    assert len(data["chapters"]) == 1
    assert data["chapters"][0]["title"] == "Beginning"


@pytest.mark.asyncio
async def test_export_novel_with_chapter_range(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="RangeExportTest", author="Author")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    for i in range(1, 6):
        chapter = Chapter(
            novel_id=novel.id,
            title=f"Chapter {i}",
            chapter_index=i,
            content=_compress_content(f"Chapter {i} content"),
            word_count=5,
        )
        db.add(chapter)
    await db.commit()

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "format": "txt", "chapter_range": "2-4"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    content = response.text
    assert "Chapter 2" in content
    assert "Chapter 3" in content
    assert "Chapter 4" in content
    assert "Chapter 1" not in content


@pytest.mark.asyncio
async def test_export_novel_invalid_chapter_range(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="InvalidRangeTest", author="Author")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "format": "txt", "chapter_range": "invalid"},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_export_novel_empty_content(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    novel = Novel(title="EmptyContentTest", author="Author")
    db.add(novel)
    await db.commit()
    await db.refresh(novel)

    chapter = Chapter(
        novel_id=novel.id,
        title="Empty Chapter",
        chapter_index=1,
        content=None,
        word_count=0,
    )
    db.add(chapter)
    await db.commit()

    response = await client.post(
        "/api/export/novel",
        json={"novel_id": str(novel.id), "format": "json"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["chapters"][0]["content"] == ""


@pytest.mark.asyncio
async def test_batch_import_requires_auth(client: AsyncClient):
    response = await client.post(
        "/api/export/import",
        json={"source": "local", "path": "/some/path"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_batch_import_unsupported_source(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/export/import",
        json={"source": "url", "urls": ["http://example.com"]},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_batch_import_nonexistent_path(client: AsyncClient, auth_headers: dict):
    response = await client.post(
        "/api/export/import",
        json={"source": "local", "path": "/nonexistent/path/12345"},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_batch_import_valid_directory(client: AsyncClient, auth_headers: dict, tmp_path):
    book_dir = tmp_path / "test_book"
    book_dir.mkdir()
    chapter_file = book_dir / "第001章_测试章节.txt"
    chapter_file.write_text("This is test chapter content.", encoding="utf-8")

    response = await client.post(
        "/api/export/import",
        json={"source": "local", "path": str(tmp_path)},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] >= 0
    assert data["skipped_count"] >= 0
    assert isinstance(data["errors"], list)
