from pydantic import Field
from src.schemas.base import BaseDTO
from datetime import datetime


class PostCreateDTO(BaseDTO):
    text: str = Field(min_length=1, max_length=2200)


class PostResponseDTO(BaseDTO):
    id: int
    author_id: int
    text: str
    created_at: datetime
    likes_count: int
    comments_count: int
    is_liked: bool
