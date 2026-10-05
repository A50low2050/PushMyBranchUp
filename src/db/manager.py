from types import TracebackType

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.utils.exceptions import DBConnectionError
from src.utils.logserv import LogService

logger = LogService.get_logger()


class DBManager:
    """Класс для управления соединением с базой данных и транзакциями"""

    def __init__(
        self,
        session_factory: async_sessionmaker,
    ) -> None:
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session: AsyncSession = self.session_factory()
        # тут будут классы-репозитории для работы с таблицами
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:

        await self.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

    async def check(self) -> None:
        """Проверка соединения с базой данных"""
        try:
            await self.session.execute(text("SELECT 1"))
        except Exception as e:
            logger.error("Ошибка соединения с базой данных: %s", e)
            raise DBConnectionError("Ошибка соединения с базой данных") from e
