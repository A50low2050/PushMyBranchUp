import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.db.manager import DBManager
from src.models.base import BaseORM
from src.models.posts import PostORM
from src.models.users import UserORM
from src.schemas.comments import CommentCreateDTO, CommentDTO
from src.services.comments import CommentsService
from src.utils.exceptions import PostNotFoundError

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
