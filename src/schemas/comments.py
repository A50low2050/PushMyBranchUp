from datetime import datetime
from pydantic import Field, field_validator
from src.schemas.base import BaseDTO


class CommentCreateDTO(BaseDTO):
    content: str = Field(min_length=1, max_length=2200)

    @field_validator("content")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Комментарий не может быть пустым")
        return value


class CommentDTO(BaseDTO):
    id: int
    user_id: int
    post_id: int
    content: str
    created_at: datetime
    updated_at: datetime


class CommentAddDTO(BaseDTO):
    user_id: int
    post_id: int
    content: str


class CommentResponseDTO(BaseDTO):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    updated_at: datetime
