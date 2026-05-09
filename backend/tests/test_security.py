import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, MagicMock

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
)
from app.core.security import get_current_user
from app.core.security import oauth2_scheme
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession


class TestPasswordHashing:
    def test_password_hash_produces_different_hashes(self):
        password = "testpassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        password = "correctpassword"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "correctpassword"
        hashed = get_password_hash(password)
        assert verify_password("wrongpassword", hashed) is False

    def test_password_hash_truncation(self):
        long_password = "a" * 100
        hashed = get_password_hash(long_password)
        assert len(hashed) > 0
        assert verify_password(long_password[:72], hashed) is True

    def test_empty_password_hash(self):
        password = ""
        hashed = get_password_hash(password)
        assert len(hashed) > 0


class TestJWTTokens:
    def test_create_access_token(self):
        data = {"sub": "test-user-id"}
        token = create_access_token(data)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_verify_valid_token(self):
        data = {"sub": "test-user-id"}
        token = create_access_token(data)
        payload = verify_token(token)
        assert payload["sub"] == "test-user-id"
        assert "exp" in payload

    def test_verify_invalid_token(self):
        with pytest.raises(HTTPException) as exc_info:
            verify_token("invalid.token.here")
        assert exc_info.value.status_code == 401

    def test_token_contains_expiration(self):
        data = {"sub": "user123"}
        token = create_access_token(data)
        payload = verify_token(token)
        exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        now = datetime.now(timezone.utc)
        assert exp > now


class TestOAuth2Scheme:
    def test_oauth2_scheme_exists(self):
        assert oauth2_scheme is not None


@pytest.mark.asyncio
class TestGetCurrentUser:
    async def test_get_current_user_valid_token(self, db: AsyncSession):
        from app.models.user import User
        import uuid

        user = User(
            username="testuser",
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})

        current_user = await get_current_user(token=token, db=db)
        assert current_user.id == user.id
        assert current_user.username == "testuser"

    async def test_get_current_user_invalid_token(self, db: AsyncSession):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token="invalid-token", db=db)
        assert exc_info.value.status_code == 401

    async def test_get_current_user_expired_token(self, db: AsyncSession):
        from jose import jwt
        from app.core.config import get_settings
        settings = get_settings()

        expired_data = {
            "sub": "some-user-id",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        expired_token = jwt.encode(
            expired_data,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=expired_token, db=db)
        assert exc_info.value.status_code == 401

    async def test_get_current_user_missing_sub(self, db: AsyncSession):
        from jose import jwt
        from app.core.config import get_settings
        settings = get_settings()

        no_sub_data = {"username": "test", "exp": datetime.now(timezone.utc) + timedelta(hours=1)}
        token = jwt.encode(no_sub_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db)
        assert exc_info.value.status_code == 401

    async def test_get_current_user_invalid_uuid(self, db: AsyncSession):
        token = create_access_token(data={"sub": "not-a-valid-uuid"})

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db)
        assert exc_info.value.status_code == 401
        assert "无效的用户ID" in exc_info.value.detail

    async def test_get_current_user_nonexistent_user(self, db: AsyncSession):
        import uuid
        token = create_access_token(data={"sub": str(uuid.uuid4())})

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db)
        assert exc_info.value.status_code == 401
        assert "用户不存在" in exc_info.value.detail

    async def test_get_current_user_inactive_user(self, db: AsyncSession):
        from app.models.user import User

        user = User(
            username="inactiveuser",
            email="inactive@example.com",
            hashed_password=get_password_hash("password123"),
            is_active=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})

        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(token=token, db=db)
        assert exc_info.value.status_code == 403
        assert "已被禁用" in exc_info.value.detail
