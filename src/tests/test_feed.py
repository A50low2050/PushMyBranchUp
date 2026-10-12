"""Тесты сценариев: лента постов (feed) по подпискам."""

import pytest

pytestmark = pytest.mark.feed


class TestFeed:
    """Сценарии получения ленты постов."""

    async def test_feed_shows_posts_from_followed(
        self, client, second_user_headers, follow_author, multiple_posts
    ):
        """Фид подписчика показывает посты автора, на которого он подписан."""
        response = await client.get(
            "/v1/posts/feed", headers=second_user_headers["headers"]
        )
        assert response.status_code == 200, response.text

        body = response.json()
        assert len(body["data"]) == 5
        author_ids = {post["user_id"] for post in body["data"]}
        assert author_ids == {multiple_posts[0]["user_id"]}

    async def test_feed_empty_without_subscriptions(
        self, client, second_user_headers, multiple_posts
    ):
        """Без подписок фид пустой, даже если в системе есть посты."""
        response = await client.get(
            "/v1/posts/feed", headers=second_user_headers["headers"]
        )
        assert response.status_code == 200, response.text
        assert response.json()["data"] == []

    async def test_feed_pagination(
        self, client, second_user_headers, follow_author, multiple_posts
    ):
        """Пагинация в фиде работает так же, как в списке постов."""
        response = await client.get(
            "/v1/posts/feed?limit=2&offset=0",
            headers=second_user_headers["headers"],
        )
        assert response.status_code == 200, response.text

        body = response.json()
        assert len(body["data"]) == 2
        assert body["per_page"] == 2
        assert body["total_pages"] == 3  # ceil(5 / 2)
        assert body["page"] == 1

    async def test_feed_unauthorized(self, client):
        """Фид без токена возвращает 401."""
        response = await client.get("/v1/posts/feed")
        assert response.status_code == 401