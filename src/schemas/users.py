from datetime import datetime
from typing import Optional

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
    email: EmailStr = Field(
        description="Электронная почта, указанная при регистрации.",
        examples=["alex@example.com"],
    )
    password: str = Field(
        min_length=1,
        description="Пароль пользователя.",
        examples=["ExamplePass123!"],
    )


class UserRegisterDTO(BaseDTO):
    username: str = Field(
        min_length=3,
        max_length=255,
        description="Имя пользователя, от 3 до 255 символов.",
        examples=["alex"],
    )
    email: EmailStr = Field(
        max_length=255,
        description="Адрес электронной почты.",
        examples=["alex@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Пароль, от 8 до 128 символов.",
        examples=["ExamplePass123!"],
    )


class UserResponseDTO(BaseDTO):
    id: int = Field(description="Уникальный ID пользователя")
    username: str = Field(description="Имя пользователя")
    email: EmailStr = Field(description="Электронная почта пользователя")
    created_at: datetime = Field(description="Дата и время регистрации")
    updated_at: datetime = Field(description="Дата и время последнего изменения профиля")


class UserSingleResponseDTO(BaseDTO):
    data: UserResponseDTO


UserGetMeResponseDTO = UserSingleResponseDTO


class UserGetAllResponseDTO(BaseDTO):
    page: int
    per_page: int
    total_pages: int
    data: list[UserResponseDTO]


class UserAddDTO(BaseDTO):
    username: str
    email: EmailStr
    hashed_password: str


class UserUpdateDTO(BaseDTO):
    username: str = Field(
        min_length=3,
        max_length=255,
        description="Новое имя пользователя, от 3 до 255 символов.",
        examples=["alex_new"],
    )
