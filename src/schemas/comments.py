from datetime import datetime
from pydantic import Field
from src.schemas.base import BaseDTO


class CommentCreateDTO(BaseDTO):
    text: str = Field(min_length=1, max_length=2200)


class CommentResponseDTO(BaseDTO):
    id: int
    post_id: int
    author_id: int
    text: str
    created_at: datetime
