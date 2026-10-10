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

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
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
from src.models.base import BaseORM
from src.utils.cacheserv import InMemoryAsyncCacheService

# Регистрируем все таблицы в metadata
from src.models import (  # noqa: F401
    comments,
    likes,
    posts,
    subscriptions,
    tokens,
    users,
)

test_engine = create_async_engine(os.environ["ENV_DATABASE__URL"], echo=False)

# Включаем foreign keys в тестовой БД
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
    if os.path.exists(TEST_DB_FILE):
        os.remove(TEST_DB_FILE)


@pytest_asyncio.fixture(autouse=True)
async def _clean_tables():
    """Чистим все таблицы после каждого теста — изоляция тестов."""
    yield
    async with test_engine.begin() as conn:
        for table in reversed(BaseORM.metadata.sorted_tables):
            await conn.execute(table.delete())


@pytest_asyncio.fixture
async def client():
    """httpx-клиент поверх app с подменой БД и кеша."""

    async def _override_get_db():
        async with DBManager(async_test_sessionmaker) as db:
            yield db

    cache_instance = InMemoryAsyncCacheService()

    async def _override_cache():
        return cache_instance

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_cache] = _override_cache

    app.state.cache = cache_instance

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
    del app.state.cache


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
    assert response.status_code == 200, response.text
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
