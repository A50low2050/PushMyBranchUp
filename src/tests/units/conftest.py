"""Фикстуры для юнит-тестов сервисов.

fake_notifications и fake_background_tasks — лёгкие заглушки,
которые полностью заменяют реальный NotificationService и BackgroundTasks
в тестах, не делая ни одного сетевого вызова.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.utils.notiserv import NotificationService


@pytest.fixture
def fake_notifications() -> NotificationService:
    """Заглушка NotificationService: notify() — корутина-пустышка."""
    mock = MagicMock(spec=NotificationService)
    mock.notify = AsyncMock(return_value=None)
    return mock  # type: ignore[return-value]


@pytest.fixture
def fake_background_tasks():
    """
    Заглушка BackgroundTasks: add_task() запоминает вызовы, но ничего не выполняет.
    """
    mock = MagicMock()
    mock.add_task = MagicMock()
    return mock


@pytest.fixture
def fake_payload() -> MagicMock:
    """Заглушка AccessTokenPayloadDTO для тестов сервисов."""
    mock = MagicMock()
    mock.sub = "1"
    mock.username = "tester"
    mock.email = "tester@example.com"
    return mock
