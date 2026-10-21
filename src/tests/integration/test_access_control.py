"""Тест логики закрытых токеном/открытых действий и Сваггер"""

from __future__ import annotations

import re

from httpx import AsyncClient, Response


def _substitute_path_params(path: str) -> str:
    """Заменяет {param} на 1 для тестовых запросов."""
    return re.sub(r"\{[^}]+\}", "1", path)


class TestOpenApiSecurityScheme:
    async def test_openapi_has_security_schemes(self, client: AsyncClient) -> None:
        """Swagger должен знать о security-схеме, иначе кнопка Authorize бесполезна."""
        resp: Response = await client.get("/openapi.json")
        assert resp.status_code == 200, resp.text
        schema = resp.json()
        components = schema.get("components", {})
        sec_schemes = components.get("securitySchemes", {})
        assert sec_schemes, (
            "FINDING: /openapi.json has no securitySchemes -> Swagger 'Authorize' "
            "button won't work; JWT endpoints cannot be tested via UI"
        )

    async def test_private_endpoints_declare_security_in_openapi(
        self, client: AsyncClient
    ) -> None:
        """Критические приватные роуты обязаны нести 'security: [...]' в OpenAPI."""
        resp: Response = await client.get("/openapi.json")
        assert resp.status_code == 200, resp.text
        schema = resp.json()
        paths = schema.get("paths", {})

        critical_private = [
            ("POST", "/v1/posts"),
            ("GET", "/v1/users/me"),
            ("GET", "/v1/feed"),
            ("POST", "/v1/auth/logout"),
        ]

        missing: list[str] = []
        for method, path in critical_private:
            if path not in paths:
                continue
            operation = paths[path].get(method.lower())
            if not operation or "security" not in operation:
                missing.append(f"{method} {path}")

        assert not missing, (
            f"critical private endpoints without 'security' in OpenAPI: {missing}; "
            f"Swagger won't show lock icon"
        )


class TestAccessControlConsistency:

    async def test_protected_endpoints_reject_unauthenticated(
        self, client: AsyncClient
    ) -> None:
        """Операции, требующие auth по спеке, обязаны отвергать анонимов (401/403).

        Требует auth = есть 'security' БЕЗ пустой опции {}. Операции с пустой
        опцией (optional auth) легально доступны анонимно и здесь не проверяются.
        """
        resp: Response = await client.get("/openapi.json")
        assert resp.status_code == 200, resp.text
        schema = resp.json()
        paths = schema.get("paths", {})

        leaks: list[str] = []
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method not in ("get", "post", "put", "patch", "delete"):
                    continue
                security = operation.get("security")
                if not security or any(option == {} for option in security):
                    continue
                probe: Response = await client.request(
                    method.upper(), _substitute_path_params(path)
                )
                if probe.status_code not in (401, 403):
                    leaks.append(f"{method.upper()} {path} -> {probe.status_code}")

        assert not leaks, (
            f"endpoints marked 'security' in OpenAPI are accessible without "
            f"token (lock in Swagger but no enforcement): {leaks}"
        )

    async def test_public_endpoints_do_not_require_token(
        self, client: AsyncClient
    ) -> None:
        """Операции, разрешающие анонимов по спеке, не должны отдавать 401/403.

        Разрешает анонимов = нет 'security' ИЛИ есть пустая опция {} (optional
        auth). Операции с обязательным auth проверяются соседним тестом.
        """
        resp: Response = await client.get("/openapi.json")
        assert resp.status_code == 200, resp.text
        schema = resp.json()
        paths = schema.get("paths", {})
        global_security = schema.get("security")

        false_positives: list[str] = []
        for path, methods in paths.items():
            for method, operation in methods.items():
                if method not in ("get", "post", "put", "patch", "delete"):
                    continue
                security = operation.get("security", global_security)
                if security and not any(option == {} for option in security):
                    continue
                probe: Response = await client.request(
                    method.upper(), _substitute_path_params(path)
                )
                if probe.status_code in (401, 403):
                    false_positives.append(
                        f"{method.upper()} {path} -> {probe.status_code}"
                    )

        assert not false_positives, (
            f"endpoints that allow anonymous access per spec reject it in "
            f"fact: {false_positives}"
        )

    async def test_critical_private_paths_are_protected_and_documented(
        self, client: AsyncClient
    ) -> None:
        """Критические приватные роуты обязаны быть защищены И нести 'security'."""
        resp: Response = await client.get("/openapi.json")
        assert resp.status_code == 200, resp.text
        schema = resp.json()
        paths = schema.get("paths", {})

        critical_private = [
            ("POST", "/v1/posts"),
            ("GET", "/v1/users/me"),
            ("GET", "/v1/feed"),
            ("POST", "/v1/auth/logout"),
        ]

        issues: list[str] = []
        for method, path in critical_private:
            if path not in paths:
                continue
            operation = paths[path].get(method.lower())
            if not operation:
                continue
            if "security" not in operation:
                issues.append(f"{method} {path} missing 'security' in OpenAPI")
            test_path = _substitute_path_params(path)
            r: Response = await client.request(method, test_path)
            if r.status_code not in (401, 403):
                issues.append(f"{method} {path} returned {r.status_code} without token")

        assert not issues, f"critical private endpoints issues: {issues}"
