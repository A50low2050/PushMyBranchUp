import asyncio

import pytest

from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db.connection import enable_sqlite_foreign_keys
from src.db.manager import DBManager
from src.models.base import BaseORM
from src.models.comments import CommentORM
from src.models.likes import LikeORM
from src.models.posts import PostORM
from src.models.users import UserORM
from src.schemas.posts import PostEditDTO
from src.services.posts import PostsService
from src.utils.exceptions import ForbiddenError, PostNotFoundError


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


async def _prepare_db() -> DBManager:
    """Создаёт таблицы в памяти и возвращает DBManager с тестовыми данными."""
    engine = create_async_engine(TEST_DB_URL)
    event.listen(engine.sync_engine, "connect", enable_sqlite_foreign_keys)
    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    db = await DBManager(session_factory).__aenter__()  # type: ignore[no-untyped-call]

    db.session.add(
        UserORM(
            id=1,
            username="author",
            email="author@example.com",
            hashed_password="x",
        )
    )
    db.session.add(
        UserORM(id=2, username="other", email="other@example.com", hashed_password="y")
    )
    post = PostORM(id=1, user_id=1, content="Пост автора")
    db.session.add(post)
    db.session.add(CommentORM(id=1, user_id=2, post_id=1, content="Коммент"))
    db.session.add(LikeORM(id=1, user_id=2, post_id=1))
    await db.session.flush()
    return db


def test_edit_post_success() -> None:
    """Автор может успешно обновить свой пост."""

    async def run() -> None:
        db = await _prepare_db()
        service = PostsService(db)

        updated = await service.edit_post(
            user_id=1,
            post_id=1,
            data=PostEditDTO(content="Обновленный текст поста"),
        )
        assert updated.post_id == 1
        assert updated.content == "Обновленный текст поста"

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_edit_post_not_found() -> None:
    """Редактирование несуществующего поста вызывает PostNotFoundError."""

    async def run() -> None:
        db = await _prepare_db()
        service = PostsService(db)

        with pytest.raises(PostNotFoundError):
            await service.edit_post(
                user_id=1,
                post_id=999,
                data=PostEditDTO(content="Текст"),
            )

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_edit_post_forbidden_for_non_author() -> None:
    """Попытка изменения чужого поста вызывает ForbiddenError."""

    async def run() -> None:
        db = await _prepare_db()
        service = PostsService(db)

        with pytest.raises(ForbiddenError):
            await service.edit_post(
                user_id=2,  # не автор
                post_id=1,
                data=PostEditDTO(content="Взлом"),
            )

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_delete_post_success() -> None:
    """Успешное удаление поста автором с каскадным удалением лайков и комментов."""

    async def run() -> None:
        db = await _prepare_db()
        service = PostsService(db)

        result = await service.delete_post(post_id=1, user_id=1)
        assert result.posts == 1
        assert result.comments == 1
        assert result.likes == 1

        post = await db.posts.get_one_or_none(id=1)
        assert post is None
        comms = await db.comments.get_all_filtered(post_id=1)
        assert len(comms) == 0
        likes = await db.likes.get_all_filtered(post_id=1)
        assert len(likes) == 0

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_delete_post_not_found() -> None:
    """Удаление несуществующего поста вызывает PostNotFoundError."""

    async def run() -> None:
        db = await _prepare_db()
        service = PostsService(db)

        with pytest.raises(PostNotFoundError):
            await service.delete_post(post_id=999, user_id=1)

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_delete_post_forbidden_for_non_author() -> None:
    """Попытка удаления чужого поста вызывает ForbiddenError."""

    async def run() -> None:
        db = await _prepare_db()
        service = PostsService(db)

        with pytest.raises(ForbiddenError):
            await service.delete_post(post_id=1, user_id=2)

        await db.__aexit__(None, None, None)

    asyncio.run(run())
