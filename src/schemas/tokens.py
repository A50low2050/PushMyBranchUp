from datetime import datetime

from src.schemas.base import BaseDTO


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
    expires_at: int
    access_jti: str
    created_at: int
    updated_at: int
