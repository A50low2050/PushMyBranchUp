import asyncio
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from src.config import settings
from src.utils.logserv import LogService

logger = LogService.get_logger(__name__)


class NotificationStrategy(ABC):
    @abstractmethod
    async def send(self) -> bool: ...

    @staticmethod
    @abstractmethod
    async def ping(client) -> bool: ...


class EmailMessage(NotificationStrategy):
    def __init__(
        self, recipient_email: str, subject: str, body: str, client: aiosmtplib.SMTP
    ) -> None:
        self.recipient_email = recipient_email
        self.subject = subject
        self.body = body
        self.client = client

    def __repr__(self) -> str:
        return f"EmailMessage({self.recipient_email}, {self.subject}, {self.body})"

    def _build_msg(self) -> MIMEMultipart:
        message = MIMEMultipart()
        message["From"] = settings.notifications.email.from_email
        message["To"] = self.recipient_email
        message["Subject"] = self.subject
        message.attach(MIMEText(self.body, "plain", "utf-8"))
        return message

    async def send(self) -> bool:
        message = self._build_msg()

        try:
            await self.client.send_message(
                message,
                sender=settings.notifications.email.from_email,
                recipients=[self.recipient_email],
            )
            logger.info("Успешно отправлено %s", repr(self))
        except Exception as exc:
            logger.error(
                "Ошибка при отправке %s: %s",
                repr(self),
                exc,
            )
            return False
        return True

    @staticmethod
    async def ping(client: aiosmtplib.SMTP) -> bool:
        try:
            async with client:
                username = settings.notifications.email.user
                password = settings.notifications.email.password

                await client.login(
                    username,
                    password.get_secret_value(),
                )

                logger.info("авторизация в SMTP-сервере прошла успешно!")
                return True

        except (aiosmtplib.SMTPConnectError, aiosmtplib.SMTPTimeoutError) as exc:
            logger.error("Ошибка подключения или таймаут SMTP: %s", exc)
            return False
        except aiosmtplib.SMTPAuthenticationError as exc:
            logger.error("Ошибка авторизации SMTP (неверный логин/пароль): %s", exc)
            return False
        except Exception as exc:
            logger.error("Непредвиденная ошибка при проверке SMTP: %s", exc)
            return False


class NotificationService:
    def __init__(self, messages: list[NotificationStrategy]) -> None:
        self._messages = messages

    async def notify(self) -> None:
        async with asyncio.TaskGroup() as tg:
            for message in self._messages:
                tg.create_task(message.send())
