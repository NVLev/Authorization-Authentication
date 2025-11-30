import pytest
from services.auth_service import AuthService


class TestAuthService:
    """Тесты AuthService"""

    def test_password_hashing(self):
        """Тест хеширования паролей"""
        password = "test_password_123"
        hashed = AuthService.get_password_hash(password)

        assert hashed is not None
        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_password_verification(self):
        """Тест проверки паролей"""
        password = "test_password_123"
        hashed = AuthService.get_password_hash(password)

        assert AuthService.verify_password(password, hashed) is True
        assert AuthService.verify_password("wrong", hashed) is False

    def test_create_access_token(self):
        """Тест создания access токена"""
        token = AuthService.create_access_token({"sub": "123"})

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 50

    async def test_authenticate_success(self, db_session):
        """Тест успешной аутентификации"""
        result = await AuthService.authenticate(
            email="admin@test.com",
            password="admin123",
            session=db_session
        )

        assert "access_token" in result
        assert "refresh_token" in result
        assert result["token_type"] == "bearer"

