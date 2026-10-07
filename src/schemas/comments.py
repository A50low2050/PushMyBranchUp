from datetime import datetime
from pydantic import Field, field_validator
from src.schemas.base import BaseDTO


class CommentCreateDTO(BaseDTO):
    text: str = Field(min_length=1, max_length=2200)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Комментарий не может быть пустым")
        return value


class CommentResponseDTO(BaseDTO):
    id: int
    post_id: int
    author_id: int
    text: str
    created_at: datetime
