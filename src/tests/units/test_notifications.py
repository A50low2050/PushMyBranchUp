import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import FastAPI

from src.api.main import lifespan
from src.config import settings
from src.utils.notiserv import (
    BaseNotificationProvider,
    NotificationService,
    NotificationStrategy,
)


class DummyMessage(NotificationStrategy):
    provider_key = "email"

    def build(self) -> str:
        return "dummy content"


def test_notification_service_when_disabled() -> None:
    """Когда уведомления выключены, send_batch не вызывается."""

    async def run() -> None:
        mock_provider = MagicMock(spec=BaseNotificationProvider)
        mock_provider.send_batch = AsyncMock()

        service = NotificationService(
            providers={"email": mock_provider},
            enabled=False,
        )
        assert not service.enabled

        await service.notify([DummyMessage()])
        mock_provider.send_batch.assert_not_called()

    asyncio.run(run())


def test_notification_service_when_enabled() -> None:
    """Когда уведомления включены, send_batch вызывается с переданными сообщениями."""

    async def run() -> None:
        mock_provider = MagicMock(spec=BaseNotificationProvider)
        mock_provider.send_batch = AsyncMock()

        service = NotificationService(
            providers={"email": mock_provider},
            enabled=True,
        )
        assert service.enabled

        msg = DummyMessage()
        await service.notify([msg])
        mock_provider.send_batch.assert_called_once_with([msg])

    asyncio.run(run())


def test_notification_service_toggle_at_runtime() -> None:
    """Переключатель enabled можно изменять во время выполнения программы."""

    async def run() -> None:
        mock_provider = MagicMock(spec=BaseNotificationProvider)
        mock_provider.send_batch = AsyncMock()

        service = NotificationService(
            providers={"email": mock_provider},
            enabled=True,
        )
        service.enabled = False
        assert not service.enabled

        msg = DummyMessage()
        await service.notify([msg])
        mock_provider.send_batch.assert_not_called()

        service.enabled = True
        assert service.enabled
        await service.notify([msg])
        mock_provider.send_batch.assert_called_once_with([msg])

    asyncio.run(run())


def test_lifespan_notifications_disabled_in_config() -> None:
    """При enabled=False в конфиге SMTP не опрашивается, уведомления отключены."""

    async def run() -> None:
        test_app = FastAPI()

        with (
            patch("src.api.main.DBManager") as mock_db,
            patch("src.api.main.InMemoryAsyncCacheService") as mock_cache,
            patch("src.api.main.SMTPProvider") as mock_smtp,
            patch.object(settings.notifications, "enabled", False),
        ):
            mock_db_instance = AsyncMock()
            mock_db_instance.check = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_db_instance

            mock_cache_instance = AsyncMock()
            mock_cache_instance.ping = AsyncMock()
            mock_cache.return_value = mock_cache_instance

            async with lifespan(test_app):
                assert hasattr(test_app.state, "notifications")
                assert not test_app.state.notifications.enabled
                mock_smtp.assert_not_called()

    asyncio.run(run())


def test_lifespan_smtp_ping_success() -> None:
    """При успешном SMTP ping уведомления включены."""

    async def run() -> None:
        test_app = FastAPI()

        with (
            patch("src.api.main.DBManager") as mock_db,
            patch("src.api.main.InMemoryAsyncCacheService") as mock_cache,
            patch("src.api.main.SMTPProvider") as mock_smtp,
            patch.object(settings.notifications, "enabled", True),
        ):
            mock_db_instance = AsyncMock()
            mock_db_instance.check = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_db_instance

            mock_cache_instance = AsyncMock()
            mock_cache_instance.ping = AsyncMock()
            mock_cache.return_value = mock_cache_instance

            mock_smtp_instance = MagicMock()
            mock_smtp_instance.ping = AsyncMock(return_value=True)
            mock_smtp.return_value = mock_smtp_instance

            async with lifespan(test_app):
                assert hasattr(test_app.state, "notifications")
                assert test_app.state.notifications.enabled

    asyncio.run(run())


def test_lifespan_smtp_ping_fails_auto_disable() -> None:
    """При сбое SMTP ping уведомления автоматически отключаются."""

    async def run() -> None:
        test_app = FastAPI()

        with (
            patch("src.api.main.DBManager") as mock_db,
            patch("src.api.main.InMemoryAsyncCacheService") as mock_cache,
            patch("src.api.main.SMTPProvider") as mock_smtp,
            patch.object(settings.notifications, "enabled", True),
        ):
            mock_db_instance = AsyncMock()
            mock_db_instance.check = AsyncMock()
            mock_db.return_value.__aenter__.return_value = mock_db_instance

            mock_cache_instance = AsyncMock()
            mock_cache_instance.ping = AsyncMock()
            mock_cache.return_value = mock_cache_instance

            mock_smtp_instance = MagicMock()
            mock_smtp_instance.ping = AsyncMock(return_value=False)
            mock_smtp.return_value = mock_smtp_instance

            async with lifespan(test_app):
                assert hasattr(test_app.state, "notifications")
                assert not test_app.state.notifications.enabled

    asyncio.run(run())
