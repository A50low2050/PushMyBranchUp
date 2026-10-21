from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.api.docs.description import API_DESCRIPTION
from src.api.docs.swagger import create_custom_openapi, create_custom_swagger_ui
from src.api.v1 import router as v1_router
from src.api.v1.errors import RateLimitHTTPError
from src.config import settings
from src.db.connection import sessionmaker
from src.db.manager import DBManager
from src.utils.cacheserv import InMemoryAsyncCacheService
from src.utils.exceptions import SMTPConnectionError
from src.utils.limiter import limiter
from src.utils.logserv import LogService
from src.utils.notiserv import NotificationService, SMTPProvider

LogService.configurate()

logger = LogService.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    # код до запуска приложения
    logger.info("Приложение запускается...")

    logger.info("Проверка соединения с базой данных...")
    async with DBManager(sessionmaker) as db:
        await db.check()
    logger.info("Соединение с базой данных успешно установлено!")

    logger.info("Проверка подключения к кэшу...")
    cacheserv = InMemoryAsyncCacheService()
    logger.info("- используется класс %s...", cacheserv.__class__.__name__)

    await cacheserv.ping()
    logger.info("Подключение к кэшу успешно установлено!")
    app.state.cache = cacheserv
    logger.info("Проверка системы уведомлений...")
    if not settings.notifications.enabled:
        logger.warning("Система уведомлений отключена в конфигурации.")
        app.state.notifications = NotificationService(enabled=False)
    else:
        logger.info("Проверка подключения к SMTP-серверу...")
        smtp_provider = SMTPProvider()

        smtp_is_available = await smtp_provider.ping()
        if not smtp_is_available:
            if settings.notifications.auto_disable_on_error:
                logger.warning(
                    "Не удалось подключиться к SMTP-серверу. "
                    "Система уведомлений автоматически отключена."
                )
                app.state.notifications = NotificationService(enabled=False)
            else:
                raise SMTPConnectionError
        else:
            logger.info("Успешно подключено к SMTP-серверу...")
            app.state.notifications = NotificationService(
                providers={"email": smtp_provider},
                enabled=True,
            )

    yield

    logger.info("Приложение останавливается...")


app = FastAPI(
    lifespan=lifespan,
    title="Социальная сеть по заданию Хакатона",
    description=API_DESCRIPTION,
    root_path=settings.fastapi.root_path,
    docs_url=None,
)
app.state.limiter = limiter


app.openapi = create_custom_openapi(app)  # type: ignore


@app.get("/docs", include_in_schema=False)
async def swagger_ui():
    return await create_custom_swagger_ui(app)()


# Обработчики ошибок


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> JSONResponse:
    error_obj = RateLimitHTTPError(detail=f"Превышен лимит запросов: {exc.detail}")
    response = JSONResponse(
        status_code=error_obj.status_code,
        content={
            "error": error_obj.error,
            "message": error_obj.detail,
        },
    )
    if hasattr(request.app.state, "limiter") and hasattr(
        request.state, "view_rate_limit"
    ):
        response = request.app.state.limiter._inject_headers(
            response, request.state.view_rate_limit
        )
    return response


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
    logger.exception(
        "Unhandled error while processing %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "Ошибка на стороне сервера",
        },
    )


app.include_router(v1_router)
