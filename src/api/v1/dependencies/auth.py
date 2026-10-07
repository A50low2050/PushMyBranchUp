from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from src.api.v1.dependencies.cache import CacheDep
from src.api.v1.errors import (
    InvalidTokenHTTPError,
    WithdrawnTokenHTTPError,
)
from src.config import settings
from src.services.auth import TokenService

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
            raise WithdrawnTokenHTTPError

        return sub

    async def __call__(
        self,
        sub: Annotated[int, Depends(validate)],
    ) -> int:
        return sub


GetSubDep = Annotated[int, Depends(AccessTokenResolver())]
GetAccessTokenDep = Annotated[str, Depends(AccessTokenResolver.get_access_token)]
