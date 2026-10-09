"""Тесты сценариев: регистрация, вход, неверный пароль, доступ без токена."""

import pytest

from src.tests.conftest import route_path

pytestmark = pytest.mark.auth


class TestRegistration:
    """Сценарии регистрации."""

    async def test_register_success(self, client, register_payload):
        """Успешная регистрация возвращает 200 и данные пользователя."""
        response = await client.post(route_path("/auth/register"), json=register_payload)
        assert response.status_code == 200, response.text

        body = response.json()
        assert "data" in body
        assert body["data"]["username"] == register_payload["username"]
        assert body["data"]["email"] == register_payload["email"]

    async def test_register_duplicate_email(self, client, registered_user):
        """Регистрация с уже занятым email возвращает 409."""
        payload = {
            "username": "another_user",
            "email": registered_user["email"],  # уже занят
            "password": "AnotherPass123!",
        }
        response = await client.post(route_path("/auth/register"), json=payload)
        assert response.status_code == 409
        assert response.json()["error"] == "USER_ALREADY_EXISTS"

    @pytest.mark.parametrize(
        "payload",
        [
            pytest.param(
                {"username": "ab", "email": "short@example.com", "password": "Password123!"},
                id="username_too_short",
            ),
            pytest.param(
                {"username": "validuser", "email": "shortpw@example.com", "password": "short"},
                id="password_too_short",
            ),
        ],
    )
    async def test_register_validation_errors(self, client, payload):
        """Невалидные данные при регистрации возвращают 422 от pydantic."""
        response = await client.post(route_path("/auth/register"), json=payload)
        assert response.status_code == 422


class TestLogin:
    """Сценарии входа."""

    async def test_login_success(self, client, register_payload, registered_user):
        """Вход с валидными данными возвращает access- и refresh-токены.
        
        registered_user уже создан через register_payload, просто логируемся.
        """
        response = await client.post(
            route_path("/auth/login"),
            json={
                "email": register_payload["email"],
                "password": register_payload["password"],
            },
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["type"] == "Bearer"
        # Refresh-токен должен быть в cookie
        assert "refresh_token" in response.cookies

    async def test_login_wrong_password(self, client, registered_user):
        """Вход с неверным паролем возвращает 400."""
        response = await client.post(
            route_path("/auth/login"),
            json={
                "email": registered_user["email"],
                "password": "WrongPassword123!",
            },
        )
        assert response.status_code == 400
        assert response.json()["error"] == "INVALID_LOGIN_DATA"

    async def test_login_nonexistent_user(self, client):
        """Вход несуществующего пользователя возвращает 400 (пустая БД)."""
        response = await client.post(
            route_path("/auth/login"),
            json={"email": "noone@example.com", "password": "Whatever123!"},
        )
        assert response.status_code == 400


class TestAccess:
    """Сценарии доступа к защищённым эндпоинтам."""

    @pytest.mark.access
    async def test_me_forbidden_without_token(self, client):
        """GET /auth/me без заголовка Authorization возвращает 401."""
        response = await client.get(route_path("/auth/me"))
        assert response.status_code == 401

    @pytest.mark.access
    async def test_me_forbidden_with_invalid_token(self, client):
        """GET /auth/me с невалидным токеном возвращает 401."""
        response = await client.get(
            route_path("/auth/me"),
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert response.status_code == 401

    async def test_me_success_with_valid_token(self, client, auth_headers):
        """GET /auth/me с валидным токеном возвращает данные пользователя."""
        response = await client.get(route_path("/auth/me"), headers=auth_headers)
        assert response.status_code == 200, response.text

        body = response.json()
        assert "data" in body
        # Базовая проверка структуры ответа
        assert "username" in body["data"]
        assert "email" in body["data"]