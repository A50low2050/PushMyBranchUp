"""Тесты сценариев API: создание, получение, редактирование и удаление комментариев."""

from httpx import AsyncClient

from src.tests.conftest import route_path


class TestComments:
    """Сценарии работы с комментариями через API."""

    async def test_create_comment_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Успешное создание комментария к посту."""
        post_id = created_post["id"]
        response = await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Первый комментарий к посту!"},
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["content"] == "Первый комментарий к посту!"
        assert data["post_id"] == post_id
        assert "id" in data

    async def test_create_comment_missing_post(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Создание комментария к несуществующему посту возвращает 404."""
        response = await client.post(
            route_path("/posts/99999/comments"),
            headers=auth_headers,
            json={"content": "Комментарий в никуда"},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "POST_NOT_FOUND"

    async def test_get_comments_list(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Получение списка комментариев к посту."""
        post_id = created_post["id"]
        # Создаем комментарий
        await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Комментарий для списка"},
        )
        response = await client.get(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        items = response.json()
        assert isinstance(items, list)
        assert len(items) >= 1
        assert items[0]["content"] == "Комментарий для списка"

    async def test_get_comment_by_id_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Получение отдельного комментария по post_id и comment_id."""
        post_id = created_post["id"]
        create_resp = await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Точный комментарий"},
        )
        comment_id = create_resp.json()["id"]

        response = await client.get(
            route_path(f"/posts/{post_id}/comments/{comment_id}"),
            headers=auth_headers,
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["id"] == comment_id
        assert data["content"] == "Точный комментарий"

    async def test_get_comment_missing_post_returns_comment_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Если post_id неверен, возвращается COMMENT_NOT_FOUND (один запрос к БД)."""
        post_id = created_post["id"]
        create_resp = await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Тестовый комментарий"},
        )
        comment_id = create_resp.json()["id"]

        # Передаем неверный post_id:
        response = await client.get(
            route_path(f"/posts/99999/comments/{comment_id}"),
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert response.json()["error"] == "COMMENT_NOT_FOUND"

    async def test_edit_comment_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Автор успешно редактирует комментарий (PATCH и PUT)."""
        post_id = created_post["id"]
        create_resp = await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Исходный комментарий"},
        )
        comment_id = create_resp.json()["id"]

        # PATCH
        patch_resp = await client.patch(
            route_path(f"/posts/{post_id}/comments/{comment_id}"),
            headers=auth_headers,
            json={"content": "Отредактированный комментарий (PATCH)"},
        )
        assert patch_resp.status_code == 200, patch_resp.text
        assert patch_resp.json()["content"] == "Отредактированный комментарий (PATCH)"

        # PUT
        put_resp = await client.put(
            route_path(f"/posts/{post_id}/comments/{comment_id}"),
            headers=auth_headers,
            json={"content": "Отредактированный комментарий (PUT)"},
        )
        assert put_resp.status_code == 200, put_resp.text
        assert put_resp.json()["content"] == "Отредактированный комментарий (PUT)"

    async def test_edit_comment_missing_post_returns_comment_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """При неверном post_id возвращается COMMENT_NOT_FOUND (один запрос к БД)."""
        post_id = created_post["id"]
        create_resp = await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Комментарий"},
        )
        comment_id = create_resp.json()["id"]

        response = await client.patch(
            route_path(f"/posts/99999/comments/{comment_id}"),
            headers=auth_headers,
            json={"content": "Попытка изменения"},
        )
        assert response.status_code == 404
        assert response.json()["error"] == "COMMENT_NOT_FOUND"

    async def test_edit_comment_forbidden(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        second_user_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Попытка изменения чужого комментария возвращает 403 FORBIDDEN."""
        post_id = created_post["id"]
        create_resp = await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Комментарий первого автора"},
        )
        comment_id = create_resp.json()["id"]

        response = await client.patch(
            route_path(f"/posts/{post_id}/comments/{comment_id}"),
            headers=second_user_headers,
            json={"content": "Взлом чужого комментария"},
        )
        assert response.status_code == 403
        assert response.json()["error"] == "FORBIDDEN"

    async def test_delete_comment_success(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Автор успешно удаляет свой комментарий."""
        post_id = created_post["id"]
        create_resp = await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Комментарий для удаления"},
        )
        comment_id = create_resp.json()["id"]

        del_resp = await client.delete(
            route_path(f"/posts/{post_id}/comments/{comment_id}"),
            headers=auth_headers,
        )
        assert del_resp.status_code == 200, del_resp.text
        data = del_resp.json()
        assert "data" in data
        assert data["data"]["deleted_count"] == 1

        # Проверяем, что комментария больше нет
        get_resp = await client.get(
            route_path(f"/posts/{post_id}/comments/{comment_id}"),
            headers=auth_headers,
        )
        assert get_resp.status_code == 404
        assert get_resp.json()["error"] == "COMMENT_NOT_FOUND"

    async def test_delete_comment_missing_post_returns_comment_not_found(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """При удалении с неверным post_id возвращается COMMENT_NOT_FOUND."""
        post_id = created_post["id"]
        create_resp = await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Комментарий"},
        )
        comment_id = create_resp.json()["id"]

        response = await client.delete(
            route_path(f"/posts/99999/comments/{comment_id}"),
            headers=auth_headers,
        )
        assert response.status_code == 404
        assert response.json()["error"] == "COMMENT_NOT_FOUND"

    async def test_delete_comment_forbidden(
        self,
        client: AsyncClient,
        auth_headers: dict[str, str],
        second_user_headers: dict[str, str],
        created_post: dict[str, int],
    ) -> None:
        """Попытка удаления чужого комментария возвращает 403 FORBIDDEN."""
        post_id = created_post["id"]
        create_resp = await client.post(
            route_path(f"/posts/{post_id}/comments"),
            headers=auth_headers,
            json={"content": "Комментарий первого автора"},
        )
        comment_id = create_resp.json()["id"]

        response = await client.delete(
            route_path(f"/posts/{post_id}/comments/{comment_id}"),
            headers=second_user_headers,
        )
        assert response.status_code == 403
        assert response.json()["error"] == "FORBIDDEN"
