"""Тест HTTP error codes in routes."""

from __future__ import annotations

from typing import Any

from httpx import AsyncClient, Response

from src.tests.conftest import route_path


async def _probe(client: AsyncClient, method: str, path: str, **kw: Any) -> int:
    r: Response = await client.request(method, route_path(path), **kw)
    return r.status_code


async def test_no_5xx_on_expected_failures(
    client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """Доменные отказы обязаны быть 4xx, а не fall-through в 5xx."""
    body = {"content": "audit-probe-content"}
    cases: list[tuple[str, str, dict[str, Any]]] = [
        ("GET", "/posts/999999999", {}),
        ("PATCH", "/posts/999999999", {"headers": auth_headers, "json": body}),
        ("DELETE", "/posts/999999999", {"headers": auth_headers}),
        ("GET", "/posts/999999999/comments", {}),
        ("POST", "/posts/999999999/comments", {"headers": auth_headers, "json": body}),
        ("PUT", "/posts/999999999/like", {"headers": auth_headers}),
        ("GET", "/users/999999999", {"headers": auth_headers}),
        ("PUT", "/users/999999999/follow", {"headers": auth_headers}),
        ("GET", "/feed", {"headers": auth_headers}),
        ("GET", "/users/me", {"headers": auth_headers}),
        ("POST", "/auth/refresh", {}),
        ("POST", "/auth/login", {"json": {}}),
        ("POST", "/auth/register", {"json": {"email": "no"}}),
    ]
    bad: list[str] = []
    for method, path, kw in cases:
        code = await _probe(client, method, path, **kw)
        if code in (500, 502, 503, 504):
            bad.append(f"{method} {path} -> {code}")
    assert not bad, f"FINDING 5xx (незамапленное исключение): {bad}"


async def test_auth_rejects_before_body_validation(client: AsyncClient) -> None:
    """Приватные роуты без токена: обязан быть 401/403, а НЕ 422."""
    cases: list[tuple[str, str, dict[str, Any]]] = [
        ("GET", "/users/me", {}),
        ("GET", "/feed", {}),
        ("POST", "/posts", {"json": {}}),
        ("PATCH", "/posts/1", {"json": {}}),
        ("DELETE", "/posts/1", {}),
        ("POST", "/posts/1/comments", {"json": {}}),
        ("PUT", "/posts/1/like", {}),
        ("PUT", "/users/1/follow", {}),
        ("POST", "/auth/logout", {}),
        ("POST", "/auth/refresh", {}),
    ]
    shadowed: list[str] = []
    for method, path, kw in cases:
        code = await _probe(client, method, path, **kw)
        if code == 422:
            shadowed.append(f"{method} {path} -> 422 (валидация перекрыла auth)")
    assert not shadowed, f"FINDING 422-before-auth: {shadowed}"
