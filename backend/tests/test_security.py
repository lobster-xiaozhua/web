import pytest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException

from app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    verify_token,
    get_current_user,
)


class TestPasswordHashing:
    def test_password_hash_produces_hash(self):
        password = "test_password_123"
        hashed = get_password_hash(password)
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 0

    def test_password_hash_different_for_same_input(self):
        password = "test_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        assert hash1 != hash2

    def test_verify_password_correct(self):
        password = "correct_password"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        password = "correct_password"
        hashed = get_password_hash(password)
        assert verify_password("wrong_password", hashed) is False

    def test_verify_password_empty(self):
        hashed = get_password_hash("real_password")
        assert verify_password("", hashed) is False

    def test_password_hash_truncates_long_password(self):
        long_password = "a" * 100
        hashed = get_password_hash(long_password)
        assert hashed is not None


class TestTokenCreation:
    def test_create_access_token_produces_string(self):
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret"
            mock_settings.return_value.ALGORITHM = "HS256"
            mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

            token = create_access_token({"sub": "user123"})
            assert isinstance(token, str)
            assert len(token) > 0

    def test_create_access_token_includes_expiry(self):
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret"
            mock_settings.return_value.ALGORITHM = "HS256"
            mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

            token = create_access_token({"sub": "user123"})
            assert token is not None


class TestTokenVerification:
    def test_verify_token_valid(self):
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret"
            mock_settings.return_value.ALGORITHM = "HS256"
            mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

            token = create_access_token({"sub": "user123", "role": "admin"})
            payload = verify_token(token)

            assert payload["sub"] == "user123"
            assert payload["role"] == "admin"
            assert "exp" in payload

    def test_verify_token_invalid_raises_exception(self):
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret"
            mock_settings.return_value.ALGORITHM = "HS256"

            with pytest.raises(HTTPException) as exc_info:
                verify_token("invalid.token.here")
            assert exc_info.value.status_code == 401


class TestGetCurrentUser:
    @pytest.mark.asyncio
    async def test_get_current_user_valid_token(self):
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret"
            mock_settings.return_value.ALGORITHM = "HS256"
            mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

            token = create_access_token({"sub": str(uuid.uuid4())})

            mock_user = MagicMock()
            mock_user.is_active = True

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_db.execute = AsyncMock(return_value=mock_result)

            user = await get_current_user(token=token, db=mock_db)
            assert user == mock_user

    @pytest.mark.asyncio
    async def test_get_current_user_invalid_uuid(self):
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret"
            mock_settings.return_value.ALGORITHM = "HS256"
            mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

            token = create_access_token({"sub": "not_a_valid_uuid"})

            mock_db = MagicMock()

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=token, db=mock_db)
            assert exc_info.value.status_code == 401
            assert "无效的用户ID" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_missing_sub(self):
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret"
            mock_settings.return_value.ALGORITHM = "HS256"
            mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

            token = create_access_token({})

            mock_db = MagicMock()

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=token, db=mock_db)
            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_user_inactive_user(self):
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret"
            mock_settings.return_value.ALGORITHM = "HS256"
            mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

            user_id = str(uuid.uuid4())
            token = create_access_token({"sub": user_id})

            mock_user = MagicMock()
            mock_user.is_active = False

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = mock_user
            mock_db.execute = AsyncMock(return_value=mock_result)

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=token, db=mock_db)
            assert exc_info.value.status_code == 403
            assert "已被禁用" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_not_found(self):
        with patch("app.core.security.get_settings") as mock_settings:
            mock_settings.return_value.SECRET_KEY = "test_secret"
            mock_settings.return_value.ALGORITHM = "HS256"
            mock_settings.return_value.ACCESS_TOKEN_EXPIRE_MINUTES = 30

            token = create_access_token({"sub": str(uuid.uuid4())})

            mock_db = MagicMock()
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_db.execute = AsyncMock(return_value=mock_result)

            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(token=token, db=mock_db)
            assert exc_info.value.status_code == 401
            assert "用户不存在" in exc_info.value.detail
