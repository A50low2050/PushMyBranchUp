from datetime import datetime

from src.schemas.base import BaseDTO


class LikeResponseDTO(BaseDTO):
    post_id: int
    user_id: int
    is_liked: bool


class LikeAddDTO(BaseDTO):
    user_id: int
    post_id: int


class LikeDTO(BaseDTO):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    updated_at: datetime
