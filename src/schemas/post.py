from datetime import datetime
from src.schemas.base import BaseDTO


class PostDTO(BaseDTO):
    id: int
    author_id: int
    title: str
    text: str
    created_at: datetime
    updated_at: datetime
