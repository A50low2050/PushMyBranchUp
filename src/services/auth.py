import uuid
from datetime import UTC, datetime

import jwt

from src.config import settings
from src.schemas.tokens import (
    CreatedAccessToken,
    CreatedRefreshTokenDTO,
    IssuedTokens,
    RefreshTokenCreateDTO,
    RefreshTokenDTO,
)
from src.schemas.users import UserDTO
from src.services.base import BaseService
from src.utils.hashserv import HashService


class TokenService(BaseService):
    @classmethod
    def create_access_token(cls, payload: dict) -> CreatedAccessToken:
        token_data = payload.copy()
        now = datetime.now(UTC)
        expires = now + settings.auth.access_token_expire_delta
        expires_timestamp = datetime.timestamp(expires)

        jti = uuid.uuid4().hex
        token_data["jti"] = jti

        token_data["exp"] = expires_timestamp
        token_data["iat"] = datetime.timestamp(now)

        token = jwt.encode(
            payload=token_data,
            key=settings.auth.secret_key.get_secret_value(),
            algorithm=settings.auth.algorithm,
        )

        data = CreatedAccessToken(
            value=token,
            expires_at=expires,
            jti=jti,
        )

        return data

    @classmethod
    def create_refresh_token(cls) -> CreatedRefreshTokenDTO:
        now = datetime.now(UTC)
        expires = now + settings.auth.refresh_token_expire_delta
        token = uuid.uuid4().hex

        data = CreatedRefreshTokenDTO(
            value=token,
            expires_at=expires,
        )
        return data

    @classmethod
    def decode_access_token(cls, token: str) -> dict:
        decoded_token = jwt.decode(
            jwt=token,
            key=settings.auth.secret_key.get_secret_value(),
            algorithms=(settings.auth.algorithm,),
        )
        return decoded_token

    # TODO: доделать когда создастся таблица с токенами
    async def get_refresh_token(self, hashed_token: str) -> RefreshTokenDTO:
        # obj = await self.db.rf_tokens.get_one(hashed_data=hashed_token)
        # return obj
        raise NotImplementedError

    async def update_tokens(
        self,
        user: UserDTO,
    ) -> IssuedTokens:

        payload = {"sub": str(user.id)}
        access_t = self.create_access_token(payload=payload)
        refresh_t = self.create_refresh_token()

        hashed_refresh_token = HashService.hash_data(refresh_t.value)

        token_to_update = RefreshTokenCreateDTO(
            hashed_data=hashed_refresh_token,
            owner_id=user.id,
            expires_at=refresh_t.expires_at,
            access_jti=access_t.jti,
        )
        await self.db.rf_tokens.delete(owner_id=user.id)
        await self.db.rf_tokens.add(token_to_update)

        tokens = IssuedTokens(
            access_token=access_t.value, refresh_token=refresh_t.value
        )

        return tokens
