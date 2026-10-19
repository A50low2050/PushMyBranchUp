from typing import Any, Callable, Coroutine

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse
from src.api.docs.swagger_assets import SWAGGER_CSS, SWAGGER_JS

from src.api.docs.errors import add_error_examples


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
