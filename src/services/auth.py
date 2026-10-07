import uuid
from datetime import UTC, datetime
from typing import Any

import jwt

from src.config import settings
from src.schemas.auth import TokenType
from src.services.base import BaseService


class TokenService(BaseService):
    @classmethod
    def create_access_token(cls, payload: dict) -> dict[str, Any]:
        token_data = payload.copy()
        now = datetime.now(UTC)
        expires = now + settings.auth.access_token_expire_delta
        expires_timestamp = datetime.timestamp(expires)

        jti = uuid.uuid4().hex
        token_data["jti"] = jti

        token_data["exp"] = expires_timestamp
        token_data["iat"] = datetime.timestamp(now)
        token_data["typ"] = TokenType.ACCESS

        token = jwt.encode(
            payload=token_data,
            key=settings.auth.secret_key.get_secret_value(),
            algorithm=settings.auth.algorithm,
        )

        data = {
            "value": token,
            "expires_at": expires,
            "jti": jti,
            "typ": TokenType.ACCESS,
        }

        return data

    @classmethod
    def create_refresh_token(cls):
        now = datetime.now(UTC)
        expires = now + settings.auth.refresh_token_expire_delta
        token = uuid.uuid4().hex

        data = {"value": token, "expires_at": expires, "typ": TokenType.REFRESH}

        return data

    @classmethod
    def decode_access_token(cls, token: str) -> dict:
        decoded_token = jwt.decode(
            jwt=token,
            key=settings.auth.secret_key.get_secret_value(),
            algorithms=(settings.auth.algorithm,),
        )
        return decoded_token
