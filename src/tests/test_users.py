"""Тесты сценариев API: получение пользователей и проверка возвращаемых структур."""

from httpx import AsyncClient

from src.tests.conftest import route_path


class TestUsers:
    """Сценарии получения пользователей и проверка контрактов ответа."""

    async def test_get_users_list(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        registered_user: dict,
    ) -> None:
        """GET /v1/users возвращает список пользователей без утечки паролей."""
        response = await client.get(
            route_path("/users"),
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) >= 1

        first_user = data["data"][0]
        assert "id" in first_user
        assert "username" in first_user
        assert "email" in first_user
        assert "created_at" in first_user
        assert "updated_at" in first_user
        # Критично: hashed_password никогда не должен возвращаться клиенту
        assert "hashed_password" not in first_user
        assert "password" not in first_user

    async def test_get_user_by_id_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        registered_user: dict,
    ) -> None:
        """GET /v1/users/{user_id} возвращает конкретного пользователя без пароля."""
        user_id = registered_user["id"]
        response = await client.get(
            route_path(f"/users/{user_id}"),
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "data" in data
        user_data = data["data"]
        assert user_data["id"] == user_id
        assert user_data["username"] == registered_user["username"]
        assert user_data["email"] == registered_user["email"]
        assert "hashed_password" not in user_data
        assert "password" not in user_data

    async def test_get_user_by_id_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
    ) -> None:
        """GET /v1/users/{user_id} для несуществующего возвращает 404 USER_NOT_FOUND."""
        response = await client.get(
            route_path("/users/99999"),
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert response.json()["error"] == "USER_NOT_FOUND"

    async def test_get_me_contract(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        registered_user: dict,
    ) -> None:
        """GET /v1/auth/me возвращает UserGetMeResponseDTO с нужными полями."""
        response = await client.get(
            route_path("/auth/me"),
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "data" in data
        assert data["data"]["id"] == registered_user["id"]
        assert data["data"]["email"] == registered_user["email"]
        assert "hashed_password" not in data["data"]
