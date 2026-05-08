import pytest
from pydantic import ValidationError

from app.schemas.user import UserCreate, UserLogin
from app.schemas.novel import NovelCreate
from app.schemas.advanced import ExportRequest, BatchImportRequest, BookmarkCreate


class TestUserSchemas:
    def test_user_create_valid(self):
        user = UserCreate(
            username="testuser",
            email="test@example.com",
            password="password123",
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_user_create_invalid_email(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="invalid-email",
                password="password123",
            )
        errors = exc_info.value.errors()
        assert any("email" in str(e).lower() for e in errors)

    def test_user_create_short_username(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",
                email="test@example.com",
                password="password123",
            )
        errors = exc_info.value.errors()
        assert any("username" in str(e).lower() for e in errors)

    def test_user_create_short_password(self):
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="testuser",
                email="test@example.com",
                password="12345",
            )
        errors = exc_info.value.errors()
        assert any("password" in str(e).lower() for e in errors)

    def test_user_login_valid(self):
        login = UserLogin(username="testuser", password="password123")
        assert login.username == "testuser"
        assert login.password == "password123"


class TestNovelSchemas:
    def test_novel_create_valid(self):
        novel = NovelCreate(title="测试小说", author="测试作者")
        assert novel.title == "测试小说"
        assert novel.author == "测试作者"
        assert novel.category == "未分类"

    def test_novel_create_empty_title(self):
        with pytest.raises(ValidationError):
            NovelCreate(title="", author="测试作者")

    def test_export_request_valid_txt(self):
        export = ExportRequest(novel_id="550e8400-e29b-41d4-a716-446655440000", format="txt")
        assert export.format == "txt"

    def test_export_request_valid_json(self):
        export = ExportRequest(
            novel_id="550e8400-e29b-41d4-a716-446655440000",
            format="json",
        )
        assert export.format == "json"

    def test_export_request_invalid_format(self):
        with pytest.raises(ValidationError):
            ExportRequest(
                novel_id="550e8400-e29b-41d4-a716-446655440000",
                format="pdf",
            )

    def test_export_request_with_chapter_range(self):
        export = ExportRequest(
            novel_id="550e8400-e29b-41d4-a716-446655440000",
            format="txt",
            chapter_range="1-10",
        )
        assert export.chapter_range == "1-10"


class TestBookmarkSchemas:
    def test_bookmark_create_valid(self):
        bookmark = BookmarkCreate(novel_id="550e8400-e29b-41d4-a716-446655440000")
        assert bookmark.novel_id is not None

    def test_bookmark_create_with_note(self):
        bookmark = BookmarkCreate(
            novel_id="550e8400-e29b-41d4-a716-446655440000",
            note="这是一条笔记",
        )
        assert bookmark.note == "这是一条笔记"


class TestBatchImportSchemas:
    def test_batch_import_local(self):
        batch = BatchImportRequest(source="local", path="/data/books")
        assert batch.source == "local"
        assert batch.path == "/data/books"

    def test_batch_import_invalid_source(self):
        with pytest.raises(ValidationError):
            BatchImportRequest(source="ftp")
