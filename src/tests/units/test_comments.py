from unittest.mock import MagicMock

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from src.db.connection import enable_sqlite_foreign_keys
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
from src.utils.notiserv import NotificationService

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
                id=1, username="tester", email="tester@example.com", hashed_password="x"
            )
        )
        db.session.add(PostORM(id=1, user_id=1, content="привет, мир!"))
        await db.session.flush()
        yield db

    await engine.dispose()


async def test_create_comment_success(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Успешное создание комментария в БД."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Отличный пост!")
    result = await service.create_comment(
        post_id=1,
        user_id=1,
        data=dto,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )

    assert result.id is not None
    assert result.post_id == 1
    assert result.user_id == 1
    assert result.content == "Отличный пост!"

    comment = await db_manager.comments.get_one_or_none(id=result.id)
    assert isinstance(comment, CommentDTO)
    assert comment.content == "Отличный пост!"


async def test_create_comment_raises_for_missing_post(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Создание комментария к несуществующему посту -> PostNotFoundError."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Комментарий к пустоте")
    with pytest.raises(PostNotFoundError):
        await service.create_comment(
            post_id=999,
            user_id=1,
            data=dto,
            notifications=fake_notifications,
            background_tasks=fake_background_tasks,
            payload=fake_payload,
        )


async def test_get_comment_success(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Успешное получение комментария по post_id и comment_id."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Комментарий 1")
    created = await service.create_comment(
        post_id=1,
        user_id=1,
        data=dto,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )

    fetched = await service.get_comment(post_id=1, comment_id=created.id)
    assert fetched.id == created.id
    assert fetched.content == "Комментарий 1"


async def test_get_comment_raises_comment_not_found_for_missing_post(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Если пост или комментарий отсутствует, возвращается CommentNotFoundError."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Комментарий 1")
    created = await service.create_comment(
        post_id=1,
        user_id=1,
        data=dto,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )

    # Несуществующий post_id -> CommentNotFoundError
    with pytest.raises(CommentNotFoundError):
        await service.get_comment(post_id=999, comment_id=created.id)

    # Несуществующий comment_id -> CommentNotFoundError
    with pytest.raises(CommentNotFoundError):
        await service.get_comment(post_id=1, comment_id=999)


async def test_update_comment_success(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Успешное изменение комментария автором."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Старый текст")
    created = await service.create_comment(
        post_id=1,
        user_id=1,
        data=dto,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )

    edit_dto = CommentEditDTO(content="Обновленный текст")
    updated = await service.update_comment(
        comment_id=created.id,
        post_id=1,
        user_id=1,
        data=edit_dto,
    )
    assert updated.id == created.id
    assert updated.content == "Обновленный текст"


async def test_update_comment_raises_comment_not_found_for_missing_post(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """При неверном post_id возвращается CommentNotFoundError (один запрос к БД)."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Текст")
    created = await service.create_comment(
        post_id=1,
        user_id=1,
        data=dto,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )

    edit_dto = CommentEditDTO(content="Новый текст")
    with pytest.raises(CommentNotFoundError):
        await service.update_comment(
            comment_id=created.id,
            post_id=999,
            user_id=1,
            data=edit_dto,
        )


async def test_update_comment_forbidden_for_non_author(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Попытка изменения комментария чужим пользователем вызывает ForbiddenError."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Текст")
    created = await service.create_comment(
        post_id=1,
        user_id=1,
        data=dto,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )

    edit_dto = CommentEditDTO(content="Попытка взлома")
    with pytest.raises(ForbiddenError):
        await service.update_comment(
            comment_id=created.id,
            post_id=1,
            user_id=2,  # другой пользователь
            data=edit_dto,
        )


async def test_delete_comment_success(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Успешное удаление комментария автором."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Удаляемый текст")
    created = await service.create_comment(
        post_id=1,
        user_id=1,
        data=dto,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )

    deleted_count = await service.delete_comment(
        comment_id=created.id,
        post_id=1,
        user_id=1,
    )
    assert deleted_count == 1

    comment = await db_manager.comments.get_one_or_none(id=created.id)
    assert comment is None


async def test_delete_comment_raises_comment_not_found_for_missing_post(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """При неверном post_id удаление вызывает CommentNotFoundError."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Текст")
    created = await service.create_comment(
        post_id=1,
        user_id=1,
        data=dto,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )

    with pytest.raises(CommentNotFoundError):
        await service.delete_comment(
            comment_id=created.id,
            post_id=999,
            user_id=1,
        )


async def test_delete_comment_forbidden_for_non_author(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Попытка удаления комментария чужим пользователем вызывает ForbiddenError."""
    service = CommentsService(db_manager)

    dto = CommentCreateDTO(content="Текст")
    created = await service.create_comment(
        post_id=1,
        user_id=1,
        data=dto,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )

    with pytest.raises(ForbiddenError):
        await service.delete_comment(
            comment_id=created.id,
            post_id=1,
            user_id=2,
        )
