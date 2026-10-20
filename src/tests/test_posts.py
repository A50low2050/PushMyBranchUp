"""Тесты сценариев: создание и удаление постов, пагинация."""

import pytest

pytestmark = pytest.mark.posts


class TestPosts:
    """Сценарии создания постов (включая границы длины)."""

    async def test_create_post_success(self, client, auth_headers, registered_user):
        """Успешное создание поста возвращает 200 и данные поста."""
        payload = {"content": "Это тестовый пост с валидным содержимым."}

        response = await client.post("/v1/posts", json=payload, headers=auth_headers)

        assert response.status_code == 200, response.text
        data = response.json()["data"]
        assert data["content"] == payload["content"]
        assert data["user_id"] == registered_user["id"]
        assert data["likes_count"] == 0
        assert data["is_liked"] is False
        assert data["comments_count"] == 0
        assert "post_id" in data
        assert data["post_id"] > 0
        assert "created_at" in data
        assert "updated_at" in data

    async def test_create_post_empty_string(self, client, auth_headers):
        """Попытка создать пост с пустой строкой возвращает 422."""
        payload = {"content": ""}

        response = await client.post("/v1/posts", json=payload, headers=auth_headers)

        assert response.status_code == 422, response.text

    async def test_create_post_whitespace_only(self, client, auth_headers):
        """Попытка создать пост из пробелов возвращает 422 (validator)."""
        payload = {"content": "   "}

        response = await client.post("/v1/posts", json=payload, headers=auth_headers)

        assert response.status_code == 422, response.text

    async def test_create_post_unauthorized(self, client):
        """Попытка создать пост без токена возвращает 401."""
        payload = {"content": "Пост без авторизации"}

        response = await client.post("/v1/posts", json=payload)

        assert response.status_code == 401, response.text

    async def test_create_post_min_length_ok(self, client, auth_headers):
        """Пост из 1 символа создаётся успешно (граница min_length)."""
        response = await client.post(
            "/v1/posts", json={"content": "а"}, headers=auth_headers
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"]["content"] == "а"

    async def test_create_post_max_length_ok(self, client, auth_headers):
        """Пост ровно 2200 символов создаётся успешно (граница max_length)."""
        content = "а" * 2200
        response = await client.post(
            "/v1/posts", json={"content": content}, headers=auth_headers
        )
        assert response.status_code == 200, response.text
        assert len(response.json()["data"]["content"]) == 2200

    async def test_create_post_too_long(self, client, auth_headers):
        """Пост из 2201 символа отклоняется с 422."""
        response = await client.post(
            "/v1/posts", json={"content": "а" * 2201}, headers=auth_headers
        )
        assert response.status_code == 422, response.text


class TestDeletePost:
    """Сценарии удаления постов через API."""

    async def test_delete_post_success(self, client, auth_headers, created_post):
        """Автор удаляет свой пост: 200, затем GET возвращает 404."""
        post_id = created_post["id"]

        response = await client.delete(f"/v1/posts/{post_id}", headers=auth_headers)
        assert response.status_code == 200, response.text
        assert "data" in response.json()

        get_resp = await client.get(f"/v1/posts/{post_id}", headers=auth_headers)
        assert get_resp.status_code == 404

    async def test_delete_post_not_found(self, client, auth_headers):
        """Удаление несуществующего поста возвращает 404."""
        response = await client.delete("/v1/posts/999999", headers=auth_headers)
        assert response.status_code == 404, response.text

    async def test_delete_post_forbidden(
        self, client, auth_headers, second_user_headers, created_post
    ):
        """Попытка удалить чужой пост возвращает 403."""
        post_id = created_post["id"]
        response = await client.delete(
            f"/v1/posts/{post_id}",
            headers=second_user_headers["headers"],
        )
        assert response.status_code == 403, response.text

    async def test_delete_post_unauthorized(self, client, created_post):
        """Удаление без токена возвращает 401."""
        post_id = created_post["id"]
        response = await client.delete(f"/v1/posts/{post_id}")
        assert response.status_code == 401, response.text

    async def test_delete_post_cascades_comments_and_likes(
        self, client, auth_headers, created_post
    ):
        """Удаление поста каскадно убирает его комментарии и лайки."""
        post_id = created_post["id"]

        comment_resp = await client.post(
            f"/v1/posts/{post_id}/comments",
            headers=auth_headers,
            json={"content": "Комментарий к удаляемому посту"},
        )
        assert comment_resp.status_code == 201, comment_resp.text
        comment_id = comment_resp.json()["id"]

        like_resp = await client.put(f"/v1/posts/{post_id}/like", headers=auth_headers)
        assert like_resp.status_code == 200, like_resp.text

        del_resp = await client.delete(f"/v1/posts/{post_id}", headers=auth_headers)
        assert del_resp.status_code == 200, del_resp.text

        get_comment = await client.get(
            f"/v1/posts/{post_id}/comments/{comment_id}",
            headers=auth_headers,
        )
        assert get_comment.status_code == 404


class TestPagination:
    """Сценарии пагинации списка постов."""

    async def test_default_pagination(self, client, auth_headers, multiple_posts):
        """GET /v1/posts без параметров возвращает первую страницу."""
        response = await client.get("/v1/posts", headers=auth_headers)
        assert response.status_code == 200, response.text

        body = response.json()
        assert body["page"] == 1
        assert body["per_page"] > 0
        assert len(body["data"]) <= body["per_page"]
        assert body["total_pages"] == (5 + body["per_page"] - 1) // body["per_page"]

    async def test_pagination_limit(self, client, auth_headers, multiple_posts):
        """limit ограничивает количество постов на странице."""
        response = await client.get("/v1/posts?limit=2", headers=auth_headers)
        assert response.status_code == 200, response.text

        body = response.json()
        assert len(body["data"]) == 2
        assert body["per_page"] == 2
        assert body["total_pages"] == 3  # ceil(5 / 2)
        assert body["page"] == 1

    async def test_pagination_offset(self, client, auth_headers, multiple_posts):
        """offset смещает выборку и пересчитывает номер страницы."""
        response = await client.get("/v1/posts?limit=2&offset=2", headers=auth_headers)
        assert response.status_code == 200, response.text

        body = response.json()
        assert body["page"] == 2
        assert len(body["data"]) == 2

    async def test_pages_do_not_overlap(self, client, auth_headers, multiple_posts):
        """Соседние страницы не пересекаются и вместе дают все посты."""
        r1 = await client.get("/v1/posts?limit=3&offset=0", headers=auth_headers)
        r2 = await client.get("/v1/posts?limit=3&offset=3", headers=auth_headers)

        ids_page1 = {p["post_id"] for p in r1.json()["data"]}
        ids_page2 = {p["post_id"] for p in r2.json()["data"]}
        all_ids = {p["post_id"] for p in multiple_posts}

        assert len(ids_page1) == 3
        assert len(ids_page2) == 2
        assert ids_page1.isdisjoint(ids_page2)
        assert ids_page1 | ids_page2 == all_ids

    async def test_pagination_offset_beyond_total(
        self, client, auth_headers, multiple_posts
    ):
        """offset больше количества постов возвращает пустой список."""
        response = await client.get(
            "/v1/posts?limit=2&offset=100", headers=auth_headers
        )
        assert response.status_code == 200, response.text

        body = response.json()
        assert body["data"] == []
        assert body["total_pages"] == 3

    async def test_pagination_unauthorized(self, client):
        """GET /v1/posts без токена возвращает 401."""
        response = await client.get("/v1/posts")
        assert response.status_code == 401, response.text
