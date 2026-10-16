# flake8: noqa
"""Общий конфиг тестирования для FastAPI + async SQLAlchemy проекта."""

import os
from typing import Any

TEST_DB_FILE = "./test_db.sqlite3"


os.environ.setdefault("ENV_AUTH__SECRET_KEY", "test-secret-key-for-pytest-only-12345")
os.environ.setdefault("ENV_UVICORN__HOST", "127.0.0.1")
os.environ.setdefault("ENV_UVICORN__PORT", "8000")
os.environ.setdefault("ENV_UVICORN__RELOAD", "false")
os.environ.setdefault("ENV_DATABASE__URL", f"sqlite+aiosqlite:///./{TEST_DB_FILE}")
os.environ.setdefault("ENV_NOTIFICATIONS__EMAIL__HOST", "smtp.test.local")
os.environ.setdefault("ENV_NOTIFICATIONS__EMAIL__PORT", "587")
os.environ.setdefault("ENV_NOTIFICATIONS__EMAIL__USER", "test@test.local")
os.environ.setdefault("ENV_NOTIFICATIONS__EMAIL__PASSWORD", "test-password-12345")
os.environ.setdefault("ENV_NOTIFICATIONS__EMAIL__FROM_EMAIL", "noreply@test.local")


import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.api.main import app
from src.api.v1.dependencies.cache import get_cache
from src.api.v1.dependencies.db import get_db
from src.db.connection import enable_sqlite_foreign_keys
from src.db.manager import DBManager
from unittest.mock import MagicMock

# Регистрируем все таблицы в metadata
from src.models import (  # noqa: F401
    comments,
    likes,
    posts,
    subscriptions,
    tokens,
    users,
)
from src.models.base import BaseORM
from src.utils.cacheserv import InMemoryAsyncCacheService

test_engine = create_async_engine(
    os.environ["ENV_DATABASE__URL"],
    echo=False,
    poolclass=NullPool,
)

event.listens_for(test_engine.sync_engine, "connect")(enable_sqlite_foreign_keys)

async_test_sessionmaker = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


def route_path(suffix: str) -> str:
    """Возвращает полный путь роута по его окончанию."""
    if suffix.startswith("/v1"):
        return suffix
    return f"/v1{suffix}"


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _setup_database():
    """Создаём свежую тестовую БД на всю сессию."""
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.create_all)
    yield
    await test_engine.dispose()


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables():
    """Чистим все таблицы после каждого теста — изоляция тестов."""
    yield
    async with test_engine.begin() as conn:
        for table in reversed(BaseORM.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def client():
    """httpx-клиент поверх app с подменой БД, кеша и уведомлений."""

    async def _override_get_db():
        async with DBManager(async_test_sessionmaker) as db:
            yield db

    cache_instance = InMemoryAsyncCacheService()

    notifications_mock = MagicMock()
    notifications_mock.send = MagicMock(return_value=None)
    notifications_mock.send_email = MagicMock(return_value=None)

    async def _override_cache():
        return cache_instance

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_cache] = _override_cache

    app.state.cache = cache_instance
    app.state.notifications = notifications_mock

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    # Cleanup
    app.dependency_overrides.clear()
    del app.state.cache
    del app.state.notifications


@pytest.fixture
def register_payload() -> dict:
    """Данные для регистрации (username min=3, password min=8)."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "StrongPass123!",
    }


@pytest_asyncio.fixture
async def registered_user(client, register_payload):
    """Регистрирует пользователя через POST /auth/register."""
    response = await client.post(
        route_path("/auth/register"),
        json=register_payload,
    )
    assert response.status_code == 201, response.text
    body = response.json()
    return body["data"]


@pytest_asyncio.fixture
async def auth_headers(
    client: AsyncClient,
    registered_user: Any,
    register_payload: Any,
) -> dict[str, str]:
    """Получает access-токен через /auth/login и возвращает заголовки."""
    response = await client.post(
        route_path("/auth/login"),
        json={
            "email": register_payload["email"],
            "password": register_payload["password"],
        },
    )
    assert response.status_code == 200, response.text
    data = response.json()
    token = data["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def created_post(registered_user):
    """Создаёт пост в тестовой БД для пользователя registered_user."""
    from src.models.posts import PostORM

    async with async_test_sessionmaker() as session:
        post = PostORM(
            user_id=registered_user["id"],
            content="Test Post Content",
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)

    return {"id": post.id, "user_id": post.user_id}


@pytest_asyncio.fixture
async def multiple_posts(client, auth_headers):
    """Создаёт 5 постов через API для тестов пагинации."""
    posts = []
    for i in range(1, 6):
        response = await client.post(
            "/v1/posts",
            json={"content": f"Пост номер {i} для теста пагинации"},
            headers=auth_headers,
        )
        assert response.status_code == 201, response.text
        posts.append(response.json()["data"])
    return posts


@pytest.fixture
def second_payload() -> dict:
    """Данные второго пользователя."""
    return {
        "username": "seconduser",
        "email": "second@example.com",
        "password": "StrongPass123!",
    }


@pytest_asyncio.fixture
async def second_user_headers(
    client: AsyncClient, second_payload: dict[str, str]
) -> dict[str, Any]:
    """Регистрирует второго пользователя и возвращает его заголовки и id."""
    reg = await client.post(route_path("/auth/register"), json=second_payload)
    assert reg.status_code == 201, reg.text
    user_id = reg.json()["data"]["id"]

    login = await client.post(
        route_path("/auth/login"),
        json={
            "email": second_payload["email"],
            "password": second_payload["password"],
        },
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    return {"headers": {"Authorization": f"Bearer {token}"}, "user_id": user_id}


@pytest_asyncio.fixture
async def follow_author(second_user_headers, registered_user):
    """Второй пользователь подписан на первого (запись напрямую в БД)."""
    from src.models.subscriptions import SubscriptionORM

    async with async_test_sessionmaker() as session:
        subscription = SubscriptionORM(
            follower_id=second_user_headers["user_id"],
            followed_id=registered_user["id"],
        )
        session.add(subscription)
        await session.commit()

    return {
        "follower_id": second_user_headers["user_id"],
        "followed_id": registered_user["id"],
    }
