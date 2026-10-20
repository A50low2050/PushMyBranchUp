from datetime import UTC, datetime
from typing import Annotated

import jwt
from fastapi import Depends, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from src.api.v1.dependencies.cache import CacheDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.errors import (
    ExpiredTokenHTTPError,
    InvalidTokenHTTPError,
    UnauthorizedHTTPError,
    WithdrawnTokenHTTPError,
)
from src.config import settings
from src.schemas.base import BaseDTO
from src.schemas.tokens import AccessTokenPayloadDTO, RefreshTokenDTO
from src.services.auth import TokenService
from src.utils.exceptions import ObjectNotFoundError
from src.utils.hashserv import HashService

security = HTTPBearer()
BearerCredentials = Annotated[HTTPAuthorizationCredentials, Depends(security)]


class AccessTokenResolver:
    @staticmethod
    def get_access_token(creds: BearerCredentials) -> str:
        return creds.credentials

    @staticmethod
    async def decode(token: str = Depends(get_access_token)) -> AccessTokenPayloadDTO:
        try:
            payload = TokenService.decode_access_token(token)
        except jwt.ExpiredSignatureError as exc:
            raise InvalidTokenHTTPError(detail="Срок действия токена истёк") from exc
        except jwt.exceptions.InvalidSignatureError as exc:
            raise InvalidTokenHTTPError(detail="Неверная подпись для токена") from exc
        except jwt.exceptions.DecodeError as exc:
            raise InvalidTokenHTTPError(detail=str(exc)) from exc

        return AccessTokenPayloadDTO(**payload)

    @staticmethod
    async def validate(
        cache: CacheDep,
        payload: Annotated[AccessTokenPayloadDTO, Depends(decode)],
    ) -> int:
        raw_sub = hasattr(payload, "sub")
        if not raw_sub:
            raise InvalidTokenHTTPError("В токене отсутствует поле 'sub'")
        try:
            sub = int(payload.sub)
        except (ValueError, TypeError) as exc:
            raise InvalidTokenHTTPError("Неверный формат 'sub' в токене") from exc

        jti = hasattr(payload, "jti")
        if not jti:
            raise InvalidTokenHTTPError("В токене отсутствует поле 'jti'")

        bl_prefix = settings.auth.access_token_blacklist_prefix
        is_blacklisted = await cache.exists(f"{bl_prefix}{payload.jti}")
        if is_blacklisted:
            raise WithdrawnTokenHTTPError("Access токен отозван")

        return sub

    async def __call__(
        self,
        sub: Annotated[int, Depends(validate)],
    ) -> int:
        return sub


class OptionalAccessTokenResolver:
    async def __call__(
        self,
        cache: CacheDep,
        creds: Annotated[
            HTTPAuthorizationCredentials | None,
            Depends(HTTPBearer(auto_error=False)),
        ],
    ) -> int | None:
        if creds is None:
            return None

        payload = await AccessTokenResolver.decode(creds.credentials)
        return await AccessTokenResolver.validate(
            cache=cache,
            payload=payload,
        )


class RefreshTokenResolver:
    @staticmethod
    def _get_refresh_token(request: Request) -> str:
        cookie = settings.cookie.key
        token = request.cookies.get(cookie)
        if not token:
            raise UnauthorizedHTTPError("Отсутствует Refresh токен в cookie")
        return token

    async def __call__(
        self,
        db: DatabaseDep,
        refresh_t: str = Depends(_get_refresh_token),
    ) -> BaseDTO:
        hashed_refresh_t = HashService.hash_data(refresh_t)
        try:
            token = await TokenService(db).get_refresh_token(hashed_refresh_t)
            current_time = datetime.now(UTC).replace(tzinfo=None)
            if token.expires_at <= current_time:
                raise ExpiredTokenHTTPError(
                    "Refresh токен устарел, пройдите авторизацию заново"
                )

        except ObjectNotFoundError as exc:
            raise WithdrawnTokenHTTPError("Refresh токен отозван") from exc
        return token


# получить id пользователя из JWT Access токена
GetSubDep = Annotated[int, Depends(AccessTokenResolver())]
# получить payload из JWT Access токена
GetAccessTokenPayloadDep = Annotated[
    AccessTokenPayloadDTO, Depends(AccessTokenResolver.decode)
]
# получить сырой Access токен
GetAccessTokenDep = Annotated[str, Depends(AccessTokenResolver.validate)]
# получить (проверить) Refresh токен в базе
GetRefreshTokenDep = Annotated[RefreshTokenDTO, Depends(RefreshTokenResolver())]
# Получить ID пользователя, если он авторизован, иначе None
GetOptionalSubDep = Annotated[int | None, Depends(OptionalAccessTokenResolver())]
