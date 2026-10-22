from collections.abc import Generator
from typing import Any

from fastapi import Request
import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app
from src.api.v1.errors import RateLimitHTTPError
from src.utils.exceptions import RateLimitError
from src.utils.limiter import limiter


@pytest.fixture(autouse=True)
def enable_rate_limiter() -> Generator[None, Any, None]:
    old = limiter.enabled
    limiter.enabled = True
    yield
    limiter.enabled = old


def test_domain_rate_limit_exceptions() -> None:
    """Проверка доменных исключений для ограничения частоты запросов."""
    domain_err = RateLimitError()
    assert "Превышен лимит запросов" in domain_err.detail

    http_err = RateLimitHTTPError()
    assert http_err.status_code == 429
    assert http_err.error == "RATE_LIMIT_EXCEEDED"
    assert "Превышен лимит запросов" in http_err.detail


@pytest.mark.asyncio
async def test_rate_limit_exceeded_blocks_requests() -> None:
    """Проверка блокировки запросов при превышении лимита (HTTP 429)."""

    @app.get("/v1/test-ratelimit-endpoint")
    @limiter.limit("2/minute")
    async def temp_endpoint(request: Request) -> dict[str, bool]:
        return {"ok": True}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        r1 = await client.get("/v1/test-ratelimit-endpoint")
        assert r1.status_code == 200

        r2 = await client.get("/v1/test-ratelimit-endpoint")
        assert r2.status_code == 200

        r3 = await client.get("/v1/test-ratelimit-endpoint")
        assert r3.status_code == 429
        body = r3.json()
        assert body["error"] == "RATE_LIMIT_EXCEEDED"
        assert body["message"] == "Превышен лимит запросов: 2 в минуту"


def test_format_rate_limit_detail() -> None:
    from src.utils.limiter import format_rate_limit_detail

    assert format_rate_limit_detail("30 per minute") == "Превышен лимит запросов: 30 в минуту"
    assert format_rate_limit_detail("30 per 1 minute") == "Превышен лимит запросов: 30 в минуту"
    assert format_rate_limit_detail("2 per 1 minute") == "Превышен лимит запросов: 2 в минуту"
    assert format_rate_limit_detail("10 per second") == "Превышен лимит запросов: 10 в секунду"
    assert format_rate_limit_detail("100 per hour") == "Превышен лимит запросов: 100 в час"
    assert format_rate_limit_detail("1000 per day") == "Превышен лимит запросов: 1000 в день"
    assert format_rate_limit_detail("5 per 10 seconds") == "Превышен лимит запросов: 5 за 10 секунд"
    assert format_rate_limit_detail("50 per 2 minutes") == "Превышен лимит запросов: 50 за 2 минуты"
    assert format_rate_limit_detail(None) == "Превышен лимит запросов. Попробуйте позже."
    assert format_rate_limit_detail("") == "Превышен лимит запросов. Попробуйте позже."
