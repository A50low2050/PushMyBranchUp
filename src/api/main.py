from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.api.v1 import router as v1_router
from src.config import settings
from src.db.connection import sessionmaker
from src.db.manager import DBManager
from src.utils.logserv import LogService

logger = LogService.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    # код до запуска приложения
    logger.info("Приложение запускается...")

    logger.info("Проверка соединения с базой данных...")
    async with DBManager(sessionmaker) as db:
        await db.check()
    logger.info("Соединение с базой данных успешно установлено!")

    yield
    logger.info("Приложение останавливается...")
    # код после завершения работы приложения


app = FastAPI(
    lifespan=lifespan,
    title=settings.fastapi.name,
    description=settings.fastapi.description,
    root_path=settings.fastapi.root_path,
)
app.include_router(v1_router)
