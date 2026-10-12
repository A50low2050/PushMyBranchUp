from datetime import datetime

from src.schemas.base import BaseDTO


class FollowResponseDTO(BaseDTO):
    follower_id: int
    followed_id: int
    followed: bool


class SubscriptionDTO(BaseDTO):
    follower_id: int
    followed_id: int
    id: int
    created_at: datetime
    updated_at: datetime


class SubscriptionAddDTO(BaseDTO):
    follower_id: int
    followed_id: int
