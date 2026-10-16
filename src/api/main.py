from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from copy import deepcopy
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, JSONResponse

from src.api.v1 import router as v1_router
from src.config import settings
from src.db.connection import sessionmaker
from src.db.manager import DBManager
from src.utils.cacheserv import InMemoryAsyncCacheService
from src.utils.exceptions import SMTPConnectionError
from src.utils.logserv import LogService
from src.utils.notiserv import NotificationService, SMTPProvider

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
    description=(
        "Документация API проекта **PushMyBranchUp**.\n\n"
        "Здесь можно проверить все реализованные API-методы социальной сети.\n\n"
        "### Работа с API\n\n"
        "Для выполнения запросов используйте **Try it out → Execute**.\n\n"
        "### Авторизация\n\n"
        "Для доступа к защищённым методам необходим JWT access-токен.\n\n"
        "1. **`POST /v1/auth/register`** — регистрация пользователя.\n"
        "2. **`POST /v1/auth/login`** — вход и получение **`access_token`**.\n"
        "3. Используйте токен в окне **Authorize**.\n\n"
        "### Обновление токена\n\n"
        "**`POST /v1/auth/refresh`** — получение нового access-токена "
        "с использованием refresh-токена, сохранённого в HttpOnly cookie."
    ),
    root_path=settings.fastapi.root_path,
    docs_url=None,
)


# Примеры ошибок в Swagger


ERROR_EXAMPLES: dict[str, dict[str, str]] = {
    "400": {
        "error": "HTTP_ERROR",
        "message": "Некорректный запрос",
    },
    "401": {
        "error": "UNAUTHORIZED",
        "message": "Требуется авторизация",
    },
    "403": {
        "error": "HTTP_ERROR",
        "message": "Недостаточно прав для выполнения операции",
    },
    "404": {
        "error": "HTTP_ERROR",
        "message": "Запрашиваемый ресурс не найден",
    },
    "405": {
        "error": "HTTP_ERROR",
        "message": "Метод не поддерживается",
    },
    "409": {
        "error": "HTTP_ERROR",
        "message": "Конфликт данных",
    },
    "422": {
        "error": "VALIDATION_ERROR",
        "message": "Invalid request data",
    },
    "429": {
        "error": "HTTP_ERROR",
        "message": "Слишком много запросов",
    },
    "500": {
        "error": "INTERNAL_SERVER_ERROR",
        "message": "Ошибка на стороне сервера",
    },
    "502": {
        "error": "HTTP_ERROR",
        "message": "Ошибка внешнего сервиса",
    },
    "503": {
        "error": "HTTP_ERROR",
        "message": "Сервис временно недоступен",
    },
}


def add_error_examples(openapi_schema: dict[str, Any]) -> None:
    """
    Добавляет конкретные примеры к уже описанным
    HTTP-ответам с ошибками.

    Не добавляет новые HTTP-коды.
    Не изменяет существующие примеры.
    Не изменяет обработку ошибок API.
    """

    paths = openapi_schema.get("paths", {})

    for path_item in paths.values():
        if not isinstance(path_item, dict):
            continue

        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue

            responses = operation.get("responses")

            if not isinstance(responses, dict):
                continue

            for status_code, response in responses.items():
                status_code = str(status_code)

                if not status_code.startswith(("4", "5")):
                    continue

                if not isinstance(response, dict):
                    continue

                # Не изменяем ответы, описанные через $ref.
                if "$ref" in response:
                    continue

                example = ERROR_EXAMPLES.get(status_code)

                if example is None:
                    continue

                content = response.get("content")

                if not isinstance(content, dict):
                    continue

                json_content = content.get("application/json")

                if not isinstance(json_content, dict):
                    continue

                # Сохраняем существующие примеры.
                if "example" in json_content:
                    continue

                if "examples" in json_content:
                    continue

                # Добавляем пример только в документацию.
                json_content["example"] = deepcopy(example)


# Заголовок и описание авторизации


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema is not None:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    security_schemes = openapi_schema.get("components", {}).get("securitySchemes", {})

    if "HTTPBearer" in security_schemes:
        security_schemes["HTTPBearer"]["description"] = (
            "### Чтобы получить токен:\n\n"
            "1. Зарегистрируйтесь через `POST /v1/auth/register`, "
            "если аккаунта ещё нет.\n"
            "2. Выполните `POST /v1/auth/login`.\n"
            "3. Скопируйте `access_token` из ответа сервера.\n"
            "4. Вставьте токен в поле ниже **без слова Bearer**."
        )

    add_error_examples(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore


# Swagger интерфейс


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui() -> HTMLResponse:
    response = get_swagger_ui_html(
        openapi_url=f"{app.root_path}{app.openapi_url}",
        title=f"{app.title} — Swagger UI",
        swagger_ui_parameters={
            "docExpansion": "list",
            "defaultModelsExpandDepth": -1,
        },
    )

    html = response.body.decode("utf-8")  # type: ignore

    custom_styles = """
    <style>
    /* Скрываем только Servers, не затрагивая Authorize */
    .swagger-ui .scheme-container .servers,
    .swagger-ui .scheme-container .servers-title {
        display: none !important;
    }

    /* Кнопка Authorize остаётся видимой */
    .swagger-ui .scheme-container .auth-wrapper {
        display: flex !important;
    }

    /* Скрываем кнопку копирования пути */
    .swagger-ui .copy-to-clipboard {
        display: none !important;
    }

    /* Скрываем надписи required и звёздочки */
    .swagger-ui span.required,
    .swagger-ui .parameter__name.required::after {
        display: none !important;
    }

    /* Скрываем колонку Links */
    .swagger-ui .responses-table th.response-col_links,
    .swagger-ui .responses-table td.response-col_links {
        display: none !important;
    }

    /* Единый размер обычного текста в описаниях методов */
    .swagger-ui .opblock-description-wrapper p,
    .swagger-ui .opblock-description-wrapper li,
    .swagger-ui .opblock-external-docs-wrapper p,
    .swagger-ui .opblock-external-docs-wrapper li,
    .swagger-ui .opblock-body .markdown p,
    .swagger-ui .opblock-body .markdown li {
        font-size: 16px !important;
        line-height: 1.5 !important;
    }
    </style>
    """

    html = html.replace("</head>", custom_styles + "</head>")

    custom_script = """
    <script>
    (function () {
        function cleanEmptyParameters() {
            document.querySelectorAll(
                '.swagger-ui .opblock-section'
            ).forEach(section => {
                const header = section.querySelector(
                    '.opblock-section-header'
                );

                if (!header) {
                    return;
                }

                const heading = header.querySelector('h4');

                if (
                    !heading ||
                    heading.textContent.trim() !== 'Parameters'
                ) {
                    return;
                }

                const container = section.querySelector(
                    '.parameters-container'
                );

                if (!container) {
                    return;
                }

                const hasRealParameters = Boolean(
                    container.querySelector(
                        'table, input, select, textarea'
                    )
                );

                const isEmpty = !hasRealParameters;

                if (isEmpty) {
                    heading.style.display = 'none';
                    container.style.display = 'none';
                } else {
                    heading.style.display = '';
                    container.style.display = '';
                }
            });
        }

        let updateScheduled = false;

        const observer = new MutationObserver(function () {
            if (updateScheduled) {
                return;
            }

            updateScheduled = true;

            requestAnimationFrame(function () {
                updateScheduled = false;
                cleanEmptyParameters();
            });
        });

        observer.observe(document.documentElement, {
            childList: true,
            subtree: true,
        });

        cleanEmptyParameters();
    })();
    </script>
    """

    html = html.replace("</body>", custom_script + "</body>")

    return HTMLResponse(content=html)


# Обработчики ошибок


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
