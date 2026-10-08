from datetime import datetime

from pydantic import EmailStr, Field

from src.schemas.base import BaseDTO


class UserDTO(BaseDTO):
    id: int
    username: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime


class UserRegisterDTO(BaseDTO):
    name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    password: str = Field(min_length=8, max_length=200)
