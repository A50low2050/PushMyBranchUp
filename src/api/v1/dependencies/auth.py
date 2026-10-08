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
    InvalidTokenHTTPError,
    UnauthorizedHTTPError,
    WithdrawnTokenHTTPError,
)
from src.config import settings
from src.schemas.base import BaseDTO
from src.schemas.tokens import RefreshTokenDTO
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
    async def decode(token: str = Depends(get_access_token)) -> dict:
        try:
            payload = TokenService.decode_access_token(token)
        except jwt.ExpiredSignatureError as exc:
            raise InvalidTokenHTTPError(detail="Срок действия токена истёк") from exc
        except jwt.exceptions.InvalidSignatureError as exc:
            raise InvalidTokenHTTPError(detail="Неверная подпись для токена") from exc
        except jwt.exceptions.DecodeError as exc:
            raise InvalidTokenHTTPError(detail=str(exc)) from exc

        return payload

    @staticmethod
    async def validate(
        cache: CacheDep,
        payload: Annotated[dict, Depends(decode)],
    ) -> int:
        sub: int | None = payload.get("sub")
        if not sub:
            raise InvalidTokenHTTPError("В токене отсутствует поле 'sub'")
        jti: str | None = payload.get("jti")
        if not jti:
            raise InvalidTokenHTTPError("В токене отсутствует поле 'jti'")

        bl_prefix = settings.auth.access_token_blacklist_prefix
        is_blacklisted = await cache.exists(f"{bl_prefix}{jti}")
        if is_blacklisted:
            raise WithdrawnTokenHTTPError("Access токен отозван")

        return sub

    async def __call__(
        self,
        sub: Annotated[int, Depends(validate)],
    ) -> int:
        return sub


class RefreshTokenResolver:
    @staticmethod
    def _get_refresh_token(request: Request) -> str:
        cookie = settings.auth.refresh_token_cookie_name
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
        except ObjectNotFoundError as exc:
            raise WithdrawnTokenHTTPError("Refresh токен отозван") from exc
        return token


GetSubDep = Annotated[int, Depends(AccessTokenResolver())]
GetAccessTokenPayloadDep = Annotated[dict, Depends(AccessTokenResolver.decode)]
GetAccessTokenDep = Annotated[str, Depends(AccessTokenResolver.validate)]
GetRefreshTokenDep = Annotated[RefreshTokenDTO, Depends(RefreshTokenResolver())]
