"""Тесты сценариев API: создание, получение, редактирование и удаление постов."""

from httpx import AsyncClient

from src.tests.conftest import route_path


class TestPosts:
    """Сценарии работы с постами через API."""

    async def test_create_post_success(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Успешное создание поста возвращает 200 и SinglePostResponseDTO."""
        response = await client.post(
            route_path("/posts"),
            headers=auth_headers,
            json={"content": "Новый интересный пост"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "data" in data
        assert data["data"]["content"] == "Новый интересный пост"
        assert data["data"]["likes_count"] == 0
        assert data["data"]["comments_count"] == 0

    async def test_get_post_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Получение существующего поста по ID."""
        post_id = created_post["id"]
        response = await client.get(
            route_path(f"/posts/{post_id}"),
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["data"]["post_id"] == post_id
        assert data["data"]["content"] == "Test Post Content"

    async def test_get_post_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Запрос несуществующего поста возвращает 404 POST_NOT_FOUND."""
        response = await client.get(
            route_path("/posts/99999"),
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert response.json()["error"] == "POST_NOT_FOUND"

    async def test_edit_post_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Автор успешно редактирует пост (PATCH и PUT)."""
        post_id = created_post["id"]
        # PATCH
        response = await client.patch(
            route_path(f"/posts/{post_id}"),
            headers=auth_headers,
            json={"content": "Отредактированный контент (PATCH)"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["data"]["content"] == "Отредактированный контент (PATCH)"
        assert data["data"]["post_id"] == post_id

        # PUT
        response_put = await client.put(
            route_path(f"/posts/{post_id}"),
            headers=auth_headers,
            json={"content": "Отредактированный контент (PUT)"},
        )
        assert response_put.status_code == 200, response_put.text
        data = response_put.json()
        assert data["data"]["content"] == "Отредактированный контент (PUT)"

    async def test_edit_post_forbidden(
        self,
        client: AsyncClient,
        second_user_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Попытка редактирования поста не автором возвращает 403 FORBIDDEN."""
        post_id = created_post["id"]
        response = await client.patch(
            route_path(f"/posts/{post_id}"),
            headers=second_user_headers,
            json={"content": "Попытка чужого редактирования"},
        )
        assert response.status_code == 403
        assert response.json()["error"] == "FORBIDDEN"

    async def test_edit_post_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Редактирование несуществующего поста возвращает 404 POST_NOT_FOUND."""
        response = await client.patch(
            route_path("/posts/99999"),
            headers=auth_headers,
            json={"content": "Новый текст"},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "POST_NOT_FOUND"

    async def test_edit_post_validation_error(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Пустой текст поста возвращает 422 валидационную ошибку."""
        post_id = created_post["id"]
        response = await client.patch(
            route_path(f"/posts/{post_id}"),
            headers=auth_headers,
            json={"content": "   "},
        )
        assert response.status_code == 422

    async def test_delete_post_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Автор успешно удаляет пост; возвращается понятный PostDeleteResponseDTO."""
        post_id = created_post["id"]
        response = await client.delete(
            route_path(f"/posts/{post_id}"),
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert "data" in data
        assert data["data"]["posts"] == 1
        assert "comments" in data["data"]
        assert "likes" in data["data"]

        # Повторный запрос должен вернуть 404
        get_resp = await client.get(
            route_path(f"/posts/{post_id}"),
            headers=auth_headers,
        )
        assert get_resp.status_code == 404

    async def test_delete_post_forbidden(
        self,
        client: AsyncClient,
        second_user_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Попытка удаления чужого поста возвращает 403 FORBIDDEN."""
        post_id = created_post["id"]
        response = await client.delete(
            route_path(f"/posts/{post_id}"),
            headers=second_user_headers,
        )
        assert response.status_code == 403
        assert response.json()["error"] == "FORBIDDEN"

    async def test_delete_post_not_found(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Удаление несуществующего поста возвращает 404 POST_NOT_FOUND."""
        response = await client.delete(
            route_path("/posts/99999"),
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert response.json()["error"] == "POST_NOT_FOUND"
