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
from src.services.likes import LikesService
from src.utils.exceptions import PostNotFoundError
from src.utils.notiserv import NotificationService

# in-memory SQLite для тестов (aiosqlite)
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
        # тестовый пользователь и пост (через ORM, даты заполнит БД)
        db.session.add(
            UserORM(
                id=1, username="tester", email="tester@example.com", hashed_password="x"
            )
        )
        db.session.add(PostORM(id=1, user_id=1, content="привет, мир!"))
        await db.session.flush()
        yield db

    await engine.dispose()


async def test_toggle_like_sets_and_removes_like(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Первый вызов ставит лайк, второй — убирает (toggle)."""
    service = LikesService(db_manager)

    # лайка нет -> ставим
    result = await service.toggle_like(
        post_id=1,
        user_id=1,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )
    assert result.is_liked is True
    assert result.post_id == 1
    assert result.user_id == 1

    like = await db_manager.likes.get_one_or_none(user_id=1, post_id=1)
    assert like is not None

    # лайк есть -> убираем
    result = await service.toggle_like(
        post_id=1,
        user_id=1,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )
    assert result.is_liked is False

    like = await db_manager.likes.get_one_or_none(user_id=1, post_id=1)
    assert like is None


async def test_toggle_like_raises_for_missing_post(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Лайк несуществующего поста -> PostNotFoundError."""
    service = LikesService(db_manager)

    with pytest.raises(PostNotFoundError):
        await service.toggle_like(
            post_id=999,
            user_id=1,
            notifications=fake_notifications,
            background_tasks=fake_background_tasks,
            payload=fake_payload,
        )


async def test_toggle_like_isolated_between_users(
    db_manager: DBManager,
    fake_notifications: NotificationService,
    fake_background_tasks: MagicMock,
    fake_payload: MagicMock,
) -> None:
    """Лайк одного пользователя не мешает лайку другого."""
    db_manager.session.add(
        UserORM(
            id=2, username="second", email="second@example.com", hashed_password="x"
        )
    )
    await db_manager.session.flush()
    service = LikesService(db_manager)

    payload_user2 = MagicMock()
    payload_user2.sub = "2"
    payload_user2.username = "second"
    payload_user2.email = "second@example.com"

    r1 = await service.toggle_like(
        post_id=1,
        user_id=1,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=fake_payload,
    )
    r2 = await service.toggle_like(
        post_id=1,
        user_id=2,
        notifications=fake_notifications,
        background_tasks=fake_background_tasks,
        payload=payload_user2,
    )

    assert r1.is_liked is True
    assert r2.is_liked is True

    # у поста теперь два лайка
    likes = await db_manager.likes.get_all()
    assert len(likes) == 2
