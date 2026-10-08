from src.schemas.base import BaseDTO


class FollowResponseDTO(BaseDTO):
    follower_id: int
    followed_id: int
