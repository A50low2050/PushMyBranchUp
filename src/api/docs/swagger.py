from typing import Any, Callable, Coroutine

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from src.api.docs.swagger_assets import SWAGGER_CSS, SWAGGER_JS

from src.api.docs.errors import add_error_examples


def _patch_openapi_security(schema: dict[str, Any]) -> None:
    """Синхронизация security-требований схемы с фактической семантикой auth.

    Поведение приложения НЕ меняется — правится только документация:
    1. Optional-auth роуты (публичное чтение с персонализацией is_liked)
       получают пустую опцию {} по спеке OpenAPI = "авторизация опциональна".
    2. Cookie-auth роут /v1/auth/refresh получает декларацию apiKey-схемы,
       чтобы Swagger показывал замок и требовал cookie при пробе из UI.
    """
    components = schema.setdefault("components", {})
    schemes = components.setdefault("securitySchemes", {})
    schemes.setdefault(
        "refreshCookie",
        {
            "type": "apiKey",
            "in": "cookie",
            "name": "refresh_token",
            "description": "Refresh-токен в HttpOnly cookie (только /v1/auth/refresh)",
        },
    )
    paths = schema.get("paths", {})

    for path in ("/v1/posts", "/v1/posts/{post_id}"):
        operation = paths.get(path, {}).get("get")
        if operation is not None:
            operation["security"] = [{"HTTPBearer": []}, {}]

    operation = paths.get("/v1/auth/refresh", {}).get("post")
    if operation is not None:
        operation["security"] = [{"refreshCookie": []}]


def create_custom_openapi(app: FastAPI) -> Callable[[], dict[str, Any]]:
    def custom_openapi() -> dict[str, Any]:
        if app.openapi_schema is not None:
            return app.openapi_schema

        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )

        security_schemes = openapi_schema.get("components", {}).get(
            "securitySchemes", {}
        )

        if "HTTPBearer" in security_schemes:
            security_schemes["HTTPBearer"]["description"] = (
                "### Чтобы получить токен:\n\n"
                "1. Зарегистрируйтесь через `POST /v1/auth/register`, "
                "если аккаунта ещё нет.\n"
                "2. Выполните `POST /v1/auth/login`.\n"
                "3. Скопируйте `access_token` из ответа сервера.\n"
                "4. Вставьте токен в поле ниже **без слова Bearer**."
            )

        _patch_openapi_security(openapi_schema)

        add_error_examples(openapi_schema)

        app.openapi_schema = openapi_schema
        return app.openapi_schema

    return custom_openapi


def create_custom_swagger_ui(
    app: FastAPI,
) -> Callable[[], Coroutine[Any, Any, HTMLResponse]]:
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

        custom_styles = "<style>" + SWAGGER_CSS.read_text(encoding="utf-8") + "</style>"

        html = html.replace("</head>", custom_styles + "</head>")

        custom_script = (
            "<script>" + SWAGGER_JS.read_text(encoding="utf-8") + "</script>"
        )

        html = html.replace("</body>", custom_script + "</body>")

        return HTMLResponse(content=html)

    return custom_swagger_ui
