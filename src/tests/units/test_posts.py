import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

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


@pytest.fixture
async def db_manager():
    """Создаёт таблицы в памяти и возвращает DBManager с тестовыми данными."""
    engine = create_async_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    event.listen(engine.sync_engine, "connect", enable_sqlite_foreign_keys)
    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with DBManager(session_factory) as db:
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
        yield db

    await engine.dispose()


async def test_edit_post_success(db_manager: DBManager) -> None:
    """Автор может успешно обновить свой пост."""
    service = PostsService(db_manager)

    updated = await service.edit_post(
        user_id=1,
        post_id=1,
        data=PostEditDTO(content="Обновленный текст поста"),
    )
    assert updated.post_id == 1
    assert updated.content == "Обновленный текст поста"


async def test_edit_post_not_found(db_manager: DBManager) -> None:
    """Редактирование несуществующего поста вызывает PostNotFoundError."""
    service = PostsService(db_manager)

    with pytest.raises(PostNotFoundError):
        await service.edit_post(
            user_id=1,
            post_id=999,
            data=PostEditDTO(content="Текст"),
        )


async def test_edit_post_forbidden_for_non_author(db_manager: DBManager) -> None:
    """Попытка изменения чужого поста вызывает ForbiddenError."""
    service = PostsService(db_manager)

    with pytest.raises(ForbiddenError):
        await service.edit_post(
            user_id=2,  # не автор
            post_id=1,
            data=PostEditDTO(content="Взлом"),
        )


async def test_delete_post_success(db_manager: DBManager) -> None:
    """Успешное удаление поста автором с каскадным удалением лайков и комментов."""
    service = PostsService(db_manager)

    result = await service.delete_post(post_id=1, user_id=1)
    assert result.post_id == 1
    assert result.deleted is True

    post = await db_manager.posts.get_one_or_none(id=1)
    assert post is None
    comms = await db_manager.comments.get_all_filtered(post_id=1)
    assert len(comms) == 0
    likes = await db_manager.likes.get_all_filtered(post_id=1)
    assert len(likes) == 0


async def test_delete_post_not_found(db_manager: DBManager) -> None:
    """Удаление несуществующего поста вызывает PostNotFoundError."""
    service = PostsService(db_manager)

    with pytest.raises(PostNotFoundError):
        await service.delete_post(post_id=999, user_id=1)


async def test_delete_post_forbidden_for_non_author(db_manager: DBManager) -> None:
    """Попытка удаления чужого поста вызывает ForbiddenError."""
    service = PostsService(db_manager)

    with pytest.raises(ForbiddenError):
        await service.delete_post(post_id=1, user_id=2)
