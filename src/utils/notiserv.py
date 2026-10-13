from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from src.config import settings
from src.utils.logserv import LogService

logger = LogService.get_logger(__name__)


class NotificationStrategy(ABC):
    """Базовый класс для данных уведомления."""

    @abstractmethod
    def build(self) -> object:
        """Построить готовый объект для передачи провайдеру."""
        ...


class EmailMessage(NotificationStrategy):
    provider_key: str = "email"

    def __init__(self, recipient_email: str, subject: str, body: str) -> None:
        self.recipient_email = recipient_email
        self.subject = subject
        self.body = body

    def __repr__(self) -> str:
        return f"EmailMessage({self.recipient_email}, {self.subject})"

    def build(self) -> MIMEMultipart:
        message = MIMEMultipart()
        message["From"] = settings.notifications.email.from_email
        message["To"] = self.recipient_email
        message["Subject"] = self.subject
        message.attach(MIMEText(self.body, "plain", "utf-8"))
        return message


class BaseNotificationProvider(ABC):

    @abstractmethod
    async def ping(self) -> bool: ...

    @abstractmethod
    async def send_batch(self, messages: list[NotificationStrategy]) -> None: ...


class SMTPProvider(BaseNotificationProvider):
    def __init__(self) -> None:
        self._cfg = settings.notifications.email

    def _make_client(self) -> aiosmtplib.SMTP:
        return aiosmtplib.SMTP(
            hostname=self._cfg.host,
            port=self._cfg.port,
            use_tls=self._cfg.use_tls,
            start_tls=self._cfg.start_tls,
            timeout=self._cfg.timeout_seconds,
        )

    async def ping(self) -> bool:
        try:
            async with self._make_client() as client:
                await client.login(
                    self._cfg.user,
                    self._cfg.password.get_secret_value(),
                )
            logger.info("Авторизация в SMTP-сервере прошла успешно!")
            return True
        except (aiosmtplib.SMTPConnectError, aiosmtplib.SMTPTimeoutError) as exc:
            logger.error("Ошибка подключения или таймаут SMTP: %s", exc)
        except aiosmtplib.SMTPAuthenticationError as exc:
            logger.error("Ошибка авторизации SMTP (неверный логин/пароль): %s", exc)
        except Exception as exc:
            logger.error("Непредвиденная ошибка при проверке SMTP: %s", exc)
        return False

    async def send_batch(self, messages: list[NotificationStrategy]) -> None:
        email_messages = [m for m in messages if isinstance(m, EmailMessage)]
        if not email_messages:
            return

        try:
            async with self._make_client() as client:
                await client.login(
                    self._cfg.user,
                    self._cfg.password.get_secret_value(),
                )
                for msg in email_messages:
                    mime = msg.build()
                    try:
                        await client.send_message(
                            mime,
                            sender=self._cfg.from_email,
                            recipients=[msg.recipient_email],
                        )
                        logger.info("Успешно отправлено %s", repr(msg))
                    except Exception as exc:
                        logger.error("Ошибка при отправке %s: %s", repr(msg), exc)
        except (aiosmtplib.SMTPConnectError, aiosmtplib.SMTPTimeoutError) as exc:
            logger.error("Не удалось подключиться к SMTP при отправке пачки: %s", exc)
        except aiosmtplib.SMTPAuthenticationError as exc:
            logger.error("Ошибка авторизации SMTP при отправке пачки: %s", exc)
        except Exception as exc:
            logger.error("Непредвиденная ошибка SMTP при отправке пачки: %s", exc)


class NotificationService:
    def __init__(self, providers: dict[str, BaseNotificationProvider]) -> None:
        self._providers = providers

    async def notify(self, messages: list[NotificationStrategy]) -> None:
        groups: dict[str, list[NotificationStrategy]] = {}
        for msg in messages:
            key = getattr(msg, "provider_key", None)
            if key and key in self._providers:
                groups.setdefault(key, []).append(msg)
            else:
                logger.warning(
                    "Нет провайдера для сообщения %r (provider_key=%r)", msg, key
                )

        for key, batch in groups.items():
            await self._providers[key].send_batch(batch)
