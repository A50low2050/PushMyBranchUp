"""Тесты сценариев: подписки на пользователей (toggle follow)."""

import pytest

pytestmark = pytest.mark.follows


class TestFollows:
    """Сценарии взаимодействия с подписками."""

    async def test_toggle_follow_success(
        self, client, auth_headers, registered_user, second_user_headers
    ):
        """Подписка на пользователя возвращает 200 и followed=True."""
        target_id = registered_user["id"]
        response = await client.put(
            f"/v1/users/{target_id}/follow",
            headers=second_user_headers["headers"],
        )
        assert response.status_code == 200, response.text

        data = response.json()
        assert data["follower_id"] == second_user_headers["user_id"]
        assert data["followed_id"] == target_id
        assert data["followed"] is True

    async def test_toggle_follow_unfollow(
        self, client, auth_headers, registered_user, second_user_headers
    ):
        """Повторный запрос отписывает: followed=False."""
        target_id = registered_user["id"]
        url = f"/v1/users/{target_id}/follow"
        headers = second_user_headers["headers"]

        first = await client.put(url, headers=headers)
        assert first.status_code == 200, first.text
        assert first.json()["followed"] is True

        second = await client.put(url, headers=headers)
        assert second.status_code == 200, second.text
        assert second.json()["followed"] is False

    async def test_toggle_follow_user_not_found(self, client, auth_headers):
        """Подписка на несуществующего пользователя возвращает 404."""
        response = await client.put("/v1/users/999999/follow", headers=auth_headers)
        assert response.status_code == 404

    async def test_toggle_follow_self(self, client, auth_headers, registered_user):
        """Подписка на самого себя возвращает 400."""
        target_id = registered_user["id"]
        response = await client.put(
            f"/v1/users/{target_id}/follow",
            headers=auth_headers,
        )
        assert response.status_code == 400

    async def test_toggle_follow_unauthorized(self, client, registered_user):
        """Подписка без токена возвращает 401."""
        target_id = registered_user["id"]
        response = await client.put(f"/v1/users/{target_id}/follow")
        assert response.status_code == 401

    async def test_follow_affects_feed(
        self, client, auth_headers, registered_user, second_user_headers, multiple_posts
    ):
        """После подписки посты автора в фиде, после отписки фид пуст."""
        target_id = registered_user["id"]
        url = f"/v1/users/{target_id}/follow"
        headers = second_user_headers["headers"]

        follow = await client.put(url, headers=headers)
        assert follow.status_code == 200, follow.text
        assert follow.json()["followed"] is True

        feed = await client.get("/v1/posts/feed", headers=headers)
        assert feed.status_code == 200, feed.text
        assert len(feed.json()["data"]) == 5

        unfollow = await client.put(url, headers=headers)
        assert unfollow.status_code == 200, unfollow.text
        assert unfollow.json()["followed"] is False

        feed_after = await client.get("/v1/posts/feed", headers=headers)
        assert feed_after.status_code == 200, feed_after.text
        assert feed_after.json()["data"] == []