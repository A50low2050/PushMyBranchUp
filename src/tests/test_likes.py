"""Тесты сценариев: лайки постов."""

import pytest

pytestmark = pytest.mark.likes


class TestLikes:
    """Сценарии взаимодействия с лайками."""

    async def test_toggle_like_success(self, client, auth_headers, created_post, registered_user):
        """Успешная постановка лайка возвращает 200 и is_liked=True."""
        post_id = created_post["id"]
        url = f"/v1/posts/{post_id}/like"

        response = await client.put(url, headers=auth_headers)

        assert response.status_code == 200, response.text
        data = response.json()
        assert data["post_id"] == post_id
        assert data["user_id"] == registered_user["id"]
        assert data["is_liked"] is True

    async def test_toggle_like_unauthorized(self, client, created_post):
        """Попытка поставить лайк без токена возвращает 401."""
        post_id = created_post["id"]
        url = f"/v1/posts/{post_id}/like"

        response = await client.put(url)

        assert response.status_code == 401

    async def test_toggle_like_post_not_found(self, client, auth_headers):
        """Попытка поставить лайк на несуществующий пост возвращает 404."""
        fake_post_id = 999999
        url = f"/v1/posts/{fake_post_id}/like"

        response = await client.put(url, headers=auth_headers)

        assert response.status_code == 404

    async def test_toggle_like_remove(self, client, auth_headers, created_post):
        """Повторный вызов toggle_like убирает лайк (is_liked=False)."""
        post_id = created_post["id"]
        url = f"/v1/posts/{post_id}/like"

        response1 = await client.put(url, headers=auth_headers)
        assert response1.status_code == 200
        assert response1.json()["is_liked"] is True

        response2 = await client.put(url, headers=auth_headers)
        assert response2.status_code == 200
        assert response2.json()["is_liked"] is False