from datetime import datetime

from pydantic import Field, field_validator

from src.schemas.base import BaseDTO


class CommentCreate(BaseDTO):
    """DTO для создания комментария (вход)."""

    text: str = Field(..., min_length=1, max_length=2000)

    @field_validator("text")
    @classmethod
    def not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Комментарий не может быть пустым")
        return v.strip()


class CommentDTO(BaseDTO):
    """DTO для ответа с комментарием (выход)."""

    id: int
    post_id: int
    author_id: int
    text: str
    created_at: datetime
    updated_at: datetime
