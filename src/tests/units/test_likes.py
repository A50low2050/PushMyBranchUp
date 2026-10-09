import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db.manager import DBManager
from src.models.base import BaseORM
from src.models.posts import PostORM
from src.models.users import UserORM
from src.services.likes import LikesService
from src.utils.exceptions import PostNotFoundError

# in-memory SQLite для тестов (aiosqlite)
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


async def _prepare_db() -> DBManager:
    """Создаёт таблицы в памяти и возвращает DBManager с тестовыми данными."""
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    db = await DBManager(session_factory).__aenter__()  # type: ignore[no-untyped-call]

    # тестовый пользователь и пост (через ORM, даты заполнит БД)
    db.session.add(
        UserORM(
            id=1, username="tester", email="tester@example.com", hashed_password="x"
        )
    )
    db.session.add(PostORM(id=1, user_id=1, content="привет, мир!"))
    await db.session.flush()
    return db


def test_toggle_like_sets_and_removes_like() -> None:
    """Первый вызов ставит лайк, второй — убирает (toggle)."""

    async def run() -> None:
        db = await _prepare_db()
        service = LikesService(db)

        # лайка нет -> ставим
        result = await service.toggle_like(post_id=1, user_id=1)
        assert result.is_liked is True
        assert result.post_id == 1
        assert result.user_id == 1

        like = await db.likes.get_one_or_none(user_id=1, post_id=1)
        assert like is not None

        # лайк есть -> убираем
        result = await service.toggle_like(post_id=1, user_id=1)
        assert result.is_liked is False

        like = await db.likes.get_one_or_none(user_id=1, post_id=1)
        assert like is None

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_toggle_like_raises_for_missing_post() -> None:
    """Лайк несуществующего поста -> PostNotFoundError."""

    async def run() -> None:
        db = await _prepare_db()
        service = LikesService(db)

        with pytest.raises(PostNotFoundError):
            await service.toggle_like(post_id=999, user_id=1)

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_toggle_like_isolated_between_users() -> None:
    """Лайк одного пользователя не мешает лайку другого."""

    async def run() -> None:
        db = await _prepare_db()
        db.session.add(
            UserORM(
                id=2, username="second", email="second@example.com", hashed_password="x"
            )
        )
        await db.session.flush()
        service = LikesService(db)

        r1 = await service.toggle_like(post_id=1, user_id=1)
        r2 = await service.toggle_like(post_id=1, user_id=2)

        assert r1.is_liked is True
        assert r2.is_liked is True

        # у поста теперь два лайка
        likes = await db.likes.get_all()
        assert len(likes) == 2

        await db.__aexit__(None, None, None)

    asyncio.run(run())
