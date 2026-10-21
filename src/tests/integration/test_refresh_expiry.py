"""Тест rfresh token."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

import pytest
from httpx import AsyncClient, Response

from src.config import settings
from src.tests.conftest import route_path


def _extract_cookie_value(headers: Any, name: str) -> str | None:
    """Вернуть значение куки `name` из заголовков Set-Cookie, или None."""
    for raw in headers.get_list("set-cookie"):
        if raw.strip().lower().startswith(f"{name}="):
            name_value = raw.split(";", 1)[0]
            _, _, value = name_value.partition("=")
            return value.strip('"')
    return None


class TestRefreshTokenExpiry:
    async def test_valid_refresh_still_succeeds(
        self,
        client: AsyncClient,
        registered_user: dict[str, Any],
        register_payload: dict[str, str],
    ) -> None:
        """Зелёный guard: валидный refresh-токен обязан отдавать 200.

        registered_user регистрирует учётку (side-effect), креды для login
        берём из register_payload. Проходит и до, и после фикса срока —
        защищает от регрессии, когда команда добавит проверку expires_at и
        случайно сломает рабочий путь.
        """
        login: Response = await client.post(
            route_path("/auth/login"),
            json={
                "email": register_payload["email"],
                "password": register_payload["password"],
            },
        )
        assert login.status_code == 200, login.text
        token = _extract_cookie_value(login.headers, "refresh_token")
        assert token is not None, login.headers.get_list("set-cookie")

        refreshed: Response = await client.post(
            route_path("/auth/refresh"),
            headers={"Cookie": f"refresh_token={token}"},
        )
        assert refreshed.status_code == 200, refreshed.text

    async def test_expired_refresh_returns_401(
        self,
        client: AsyncClient,
        registered_user: dict[str, Any],
        register_payload: dict[str, str],
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Просроченный refresh-токен обязан отдавать 401 (и удаляться из БД).
        ...
        """
        monkeypatch.setattr(
            settings.auth,
            "refresh_token_expire_delta",
            timedelta(seconds=-1),
        )

        login: Response = await client.post(
            route_path("/auth/login"),
            json={
                "email": register_payload["email"],
                "password": register_payload["password"],
            },
        )
        assert login.status_code == 200, login.text
        token = _extract_cookie_value(login.headers, "refresh_token")
        assert token is not None, login.headers.get_list("set-cookie")

        refreshed: Response = await client.post(
            route_path("/auth/refresh"),
            headers={"Cookie": f"refresh_token={token}"},
        )
        assert refreshed.status_code == 401, refreshed.text
