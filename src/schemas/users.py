from datetime import datetime

from pydantic import EmailStr, Field

from src.schemas.base import BaseDTO


class UserDTO(BaseDTO):
    id: int
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime
    updated_at: datetime


class UserLoginDTO(BaseDTO):
    email: EmailStr
    password: str = Field(min_length=1)


class UserRegisterDTO(BaseDTO):
    username: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)


class UserResponseDTO(BaseDTO):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class TokenDTO(BaseDTO):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequestDTO(BaseDTO):
    refresh_token: str = Field(min_length=1)


class UserUpdateDTO(BaseDTO):
    username: str | None = Field(default=None, min_length=3, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
