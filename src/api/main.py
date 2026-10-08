from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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


@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    error = getattr(
        exc,
        "error",
        "UNAUTHORIZED" if exc.status_code == 401 else "HTTP_ERROR",
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": error,
            "message": exc.detail,
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "error": "VALIDATION_ERROR",
            "message": "Invalid request data",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Ошибка на стороне сервера",
        },
    )


app.include_router(v1_router)
