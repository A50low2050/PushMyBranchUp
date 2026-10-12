import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db.manager import DBManager
from src.models.base import BaseORM
from src.models.posts import PostORM
from src.models.users import UserORM
from src.schemas.comments import CommentCreateDTO, CommentDTO, CommentEditDTO
from src.services.comments import CommentsService
from src.utils.exceptions import (
    CommentNotFoundError,
    ForbiddenError,
    PostNotFoundError,
)

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


async def _prepare_db() -> DBManager:
    """Создаёт таблицы в памяти и возвращает DBManager с тестовыми данными."""
    engine = create_async_engine(TEST_DB_URL)
    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    db = await DBManager(session_factory).__aenter__()  # type: ignore[no-untyped-call]

    db.session.add(
        UserORM(
            id=1, username="tester", email="tester@example.com", hashed_password="x"
        )
    )
    db.session.add(PostORM(id=1, user_id=1, content="привет, мир!"))
    await db.session.flush()
    return db


def test_create_comment_success() -> None:
    """Успешное создание комментария в БД."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Отличный пост!")
        result = await service.create_comment(post_id=1, user_id=1, data=dto)

        assert result.id is not None
        assert result.post_id == 1
        assert result.user_id == 1
        assert result.content == "Отличный пост!"

        comment = await db.comments.get_one_or_none(id=result.id)
        assert isinstance(comment, CommentDTO)
        assert comment.content == "Отличный пост!"

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_create_comment_raises_for_missing_post() -> None:
    """Создание комментария к несуществующему посту -> PostNotFoundError."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Комментарий к пустоте")
        with pytest.raises(PostNotFoundError):
            await service.create_comment(post_id=999, user_id=1, data=dto)

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_get_comment_success() -> None:
    """Успешное получение комментария по post_id и comment_id."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Комментарий 1")
        created = await service.create_comment(post_id=1, user_id=1, data=dto)

        fetched = await service.get_comment(post_id=1, comment_id=created.id)
        assert fetched.id == created.id
        assert fetched.content == "Комментарий 1"

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_get_comment_raises_comment_not_found_for_missing_post() -> None:
    """Если пост или комментарий отсутствует, возвращается CommentNotFoundError."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Комментарий 1")
        created = await service.create_comment(post_id=1, user_id=1, data=dto)

        # Несуществующий post_id -> CommentNotFoundError
        with pytest.raises(CommentNotFoundError):
            await service.get_comment(post_id=999, comment_id=created.id)

        # Несуществующий comment_id -> CommentNotFoundError
        with pytest.raises(CommentNotFoundError):
            await service.get_comment(post_id=1, comment_id=999)

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_update_comment_success() -> None:
    """Успешное изменение комментария автором."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Старый текст")
        created = await service.create_comment(post_id=1, user_id=1, data=dto)

        edit_dto = CommentEditDTO(content="Обновленный текст")
        updated = await service.update_comment(
            comment_id=created.id,
            post_id=1,
            user_id=1,
            data=edit_dto,
        )
        assert updated.id == created.id
        assert updated.content == "Обновленный текст"

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_update_comment_raises_comment_not_found_for_missing_post() -> None:
    """При неверном post_id возвращается CommentNotFoundError (один запрос к БД)."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Текст")
        created = await service.create_comment(post_id=1, user_id=1, data=dto)

        edit_dto = CommentEditDTO(content="Новый текст")
        with pytest.raises(CommentNotFoundError):
            await service.update_comment(
                comment_id=created.id,
                post_id=999,
                user_id=1,
                data=edit_dto,
            )

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_update_comment_forbidden_for_non_author() -> None:
    """Попытка изменения комментария чужим пользователем вызывает ForbiddenError."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Текст")
        created = await service.create_comment(post_id=1, user_id=1, data=dto)

        edit_dto = CommentEditDTO(content="Попытка взлома")
        with pytest.raises(ForbiddenError):
            await service.update_comment(
                comment_id=created.id,
                post_id=1,
                user_id=2,  # другой пользователь
                data=edit_dto,
            )

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_delete_comment_success() -> None:
    """Успешное удаление комментария автором."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Удаляемый текст")
        created = await service.create_comment(post_id=1, user_id=1, data=dto)

        deleted_count = await service.delete_comment(
            comment_id=created.id,
            post_id=1,
            user_id=1,
        )
        assert deleted_count == 1

        comment = await db.comments.get_one_or_none(id=created.id)
        assert comment is None

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_delete_comment_raises_comment_not_found_for_missing_post() -> None:
    """При неверном post_id удаление вызывает CommentNotFoundError."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Текст")
        created = await service.create_comment(post_id=1, user_id=1, data=dto)

        with pytest.raises(CommentNotFoundError):
            await service.delete_comment(
                comment_id=created.id,
                post_id=999,
                user_id=1,
            )

        await db.__aexit__(None, None, None)

    asyncio.run(run())


def test_delete_comment_forbidden_for_non_author() -> None:
    """Попытка удаления комментария чужим пользователем вызывает ForbiddenError."""

    async def run() -> None:
        db = await _prepare_db()
        service = CommentsService(db)

        dto = CommentCreateDTO(content="Текст")
        created = await service.create_comment(post_id=1, user_id=1, data=dto)

        with pytest.raises(ForbiddenError):
            await service.delete_comment(
                comment_id=created.id,
                post_id=1,
                user_id=2,
            )

        await db.__aexit__(None, None, None)

    asyncio.run(run())
