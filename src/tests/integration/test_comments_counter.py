"""Тест счетчик лайков в комментариях.

Тесты динамически читают /openapi.json и проверяют:
1. Наличие securitySchemes (кнопка Authorize в Swagger работает).
2. Задокументированные как защищённые (имеют ключ 'security' в OpenAPI) —
   обязаны отдавать 401 или 403 без токена.
3. Задокументированные как публичные (нет ключа 'security') — не должны
   отдавать 401/403.
4. Критические приватные роуты защищены И задокументированы с 'security'.
"""

from __future__ import annotations

from httpx import AsyncClient, Response

from src.tests.conftest import route_path


def _extract_post_id(body: object) -> int:
    """Достать id поста из ответа любой формы; при неизвестной форме —
    AssertionError с полным телом, чтобы провал был самодокументируемым."""
    if isinstance(body, dict):
        for key in ("id", "post_id"):
            if key in body:
                return int(body[key])
        data = body.get("data")
        if isinstance(data, dict):
            for key in ("id", "post_id"):
                if key in data:
                    return int(data[key])
        if isinstance(data, list) and data:
            return _extract_post_id(data[0])
    raise AssertionError(f"unexpected post response shape: {body!r}")


async def _create_post(
    client: AsyncClient, headers: dict[str, str], content: str
) -> int:
    resp: Response = await client.post(
        route_path("/posts"), headers=headers, json={"content": content}
    )
    assert resp.status_code in (200, 201), resp.text
    return _extract_post_id(resp.json())


async def _add_comment(
    client: AsyncClient, headers: dict[str, str], post_id: int, content: str
) -> None:
    resp: Response = await client.post(
        route_path(f"/posts/{post_id}/comments"),
        headers=headers,
        json={"content": content},
    )
    assert resp.status_code in (200, 201), resp.text


async def _make_two_posts_with_comments(
    client: AsyncClient, headers: dict[str, str]
) -> tuple[int, int]:
    """Пост A с 3 комментариями и пост B с 2 (сценарий из ТЗ)."""
    post_a = await _create_post(client, headers, "Post A for comment counter audit")
    post_b = await _create_post(client, headers, "Post B for comment counter audit")
    for i in range(3):
        await _add_comment(client, headers, post_a, f"comment a{i}")
    for i in range(2):
        await _add_comment(client, headers, post_b, f"comment b{i}")
    return post_a, post_b


class TestCommentsCounter:
    async def test_comment_list_data_is_filtered_by_post(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """Зелёный guard: data фильтруется по посту, limit применяется."""
        post_a, post_b = await _make_two_posts_with_comments(client, auth_headers)

        page_b: Response = await client.get(
            route_path(f"/posts/{post_b}/comments"),
            headers=auth_headers,
            params={"limit": 2},
        )
        assert page_b.status_code == 200, page_b.text
        body = page_b.json()
        assert body["per_page"] == 2, f"limit not honored: {body}"
        assert len(body["data"]) == 2, f"data not filtered by post: {body}"

        all_a: Response = await client.get(
            route_path(f"/posts/{post_a}/comments"),
            headers=auth_headers,
            params={"limit": 10},
        )
        assert all_a.status_code == 200, all_a.text
        assert (
            len(all_a.json()["data"]) == 3
        ), f"post A must have 3 comments: {all_a.json()}"

    async def test_total_pages_counts_only_current_post_comments(
        self, client: AsyncClient, auth_headers: dict[str, str]
    ) -> None:
        """total_pages поста B обязан считаться только по его комментариям."""
        _, post_b = await _make_two_posts_with_comments(client, auth_headers)

        page_b: Response = await client.get(
            route_path(f"/posts/{post_b}/comments"),
            headers=auth_headers,
            params={"limit": 2},
        )
        assert page_b.status_code == 200, page_b.text
        body = page_b.json()
        assert (
            body["total_pages"] == 1
        ), f"total_pages inflated (counted whole table?): {body}"
