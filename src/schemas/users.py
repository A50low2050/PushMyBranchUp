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
    login: str = Field(min_length=1)
    password: str = Field(min_length=1)


class UserRegisterDTO(BaseDTO):
    username: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserResponseDTO(BaseDTO):
    id: int
    username: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class TokenDTO(BaseDTO):
    access_token: str
    token_type: str = "bearer"
