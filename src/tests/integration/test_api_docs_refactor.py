"""Течст примеров ответов и запросов для API эндпоинтов в отдельные файлы и папки (например api/examples)"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any

from httpx import AsyncClient, Response

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES_PKG = "src.api.v1.examples"
EXAMPLES_DIR = ROOT / "src" / "api" / "v1" / "examples"
STYLE_DIR = ROOT / "src" / "api" / "docs"


def _count_media_examples(content: object) -> int:
    if not isinstance(content, dict):
        return 0
    count = 0
    for media in content.values():
        if isinstance(media, dict) and ("example" in media or "examples" in media):
            count += 1
    return count


def _count_openapi_examples(schema: dict[str, Any]) -> int:
    count = 0
    paths = schema.get("paths", {})
    if isinstance(paths, dict):
        for path_item in paths.values():
            if not isinstance(path_item, dict):
                continue
            for operation in path_item.values():
                if not isinstance(operation, dict):
                    continue
                if "example" in operation or "examples" in operation:
                    count += 1
                request_body = operation.get("requestBody")
                if isinstance(request_body, dict):
                    count += _count_media_examples(request_body.get("content"))
                responses = operation.get("responses")
                if isinstance(responses, dict):
                    for response in responses.values():
                        if isinstance(response, dict):
                            count += _count_media_examples(response.get("content"))
    components = schema.get("components")
    if isinstance(components, dict):
        schemas = components.get("schemas")
        if isinstance(schemas, dict):
            for schema_obj in schemas.values():
                if isinstance(schema_obj, dict) and (
                    "example" in schema_obj or "examples" in schema_obj
                ):
                    count += 1
    return count


async def test_openapi_keeps_examples(client: AsyncClient) -> None:
    """Примеры не должны потеряться при выносе в отдельные файлы."""
    resp: Response = await client.get("/openapi.json")
    assert resp.status_code == 200, resp.text
    schema: Any = resp.json()
    assert isinstance(schema, dict), f"openapi.json is not object: {type(schema)}"
    assert _count_openapi_examples(schema) > 0, (
        "FINDING: OpenAPI has no request/response examples"
    )


def test_examples_externalized_as_importable_modules() -> None:
    """Папка примеров существует и модули экспонируют данные примеров."""
    assert EXAMPLES_DIR.is_dir(), f"missing examples dir: {EXAMPLES_DIR}"

    modules = [
        importlib.import_module(f"{EXAMPLES_PKG}.{py.stem}")
        for py in sorted(EXAMPLES_DIR.glob("*.py"))
        if py.stem != "__init__"
    ]
    assert modules, f"no example modules in {EXAMPLES_DIR}"

    example_values = [
        value
        for module in modules
        for value in vars(module).values()
        if isinstance(value, (dict, list))
    ]
    assert example_values, "example modules do not expose dict/list example values"


async def test_styles_externalized_and_delivered_to_docs(client: AsyncClient) -> None:
    """Стили — отдельные непустые файлы, и их содержимое попадает в /docs.

    Доставка инлайном (<style>/<script> через read_text+replace),
    поэтому проверяем вхождение содержимого файла в HTML, а не наличие <link>/URL.
    """
    css_path = STYLE_DIR / "swagger.css"
    js_path = STYLE_DIR / "swagger.js"
    assert css_path.is_file() and css_path.read_text(encoding="utf-8").strip(), (
        f"swagger.css missing/empty: {css_path}"
    )
    assert js_path.is_file() and js_path.read_text(encoding="utf-8").strip(), (
        f"swagger.js missing/empty: {js_path}"
    )

    docs: Response = await client.get("/docs")
    assert docs.status_code == 200, docs.text
    html = docs.text
    assert css_path.read_text(encoding="utf-8").strip() in html, (
        "swagger.css not delivered to /docs"
    )
    assert js_path.read_text(encoding="utf-8").strip() in html, (
        "swagger.js not delivered to /docs"
    )