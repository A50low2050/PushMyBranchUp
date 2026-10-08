from src.schemas.base import BaseDTO
from src.schemas.posts import PostResponseDTO


class FeedResponseDTO(BaseDTO):
    posts: list[PostResponseDTO]
