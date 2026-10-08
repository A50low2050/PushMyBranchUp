from pydantic import Field, field_validator
from src.schemas.base import BaseDTO
from datetime import datetime


class PostCreateDTO(BaseDTO):
    text: str = Field(min_length=1, max_length=2200)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Пост не может быть пустым")
        return value


class PostResponseDTO(BaseDTO):
    id: int
    author_id: int
    text: str
    created_at: datetime
    likes_count: int
    comments_count: int
    is_liked: bool
