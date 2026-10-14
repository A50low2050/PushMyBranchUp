from datetime import datetime

from src.schemas.base import BaseDTO
from pydantic import Field


class RefreshTokenCreateDTO(BaseDTO):
    hashed_data: str
    owner_id: int
    expires_at: datetime
    access_jti: str


class CreatedAccessToken(BaseDTO):
    value: str
    expires_at: datetime
    jti: str


class CreatedRefreshTokenDTO(BaseDTO):
    value: str
    expires_at: datetime


class RefreshTokenDTO(BaseDTO):
    id: int
    hashed_data: str
    owner_id: int
    expires_at: datetime
    access_jti: str
    created_at: datetime
    updated_at: datetime


class IssuedTokens(BaseDTO):
    access_token: str = Field(
        description="Access-токен для авторизации запросов через кнопку Authorize.",
    )
    refresh_token: str = Field(
        description="Refresh-токен для обновления авторизации. Также сохраняется в HttpOnly cookie.",
    )
    type: str = Field(
        default="Bearer",
        description="Тип токена авторизации.",
    )
