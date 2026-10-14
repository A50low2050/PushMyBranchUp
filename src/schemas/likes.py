from datetime import datetime

from pydantic import Field

from src.schemas.base import BaseDTO


class LikeResponseDTO(BaseDTO):
    post_id: int = Field(
        description="ID поста, которому поставили или с которого убрали лайк."
    )
    user_id: int = Field(
        description="ID пользователя, который поставил или убрал лайк."
    )
    is_liked: bool = Field(
        description="True — лайк поставлен, False — лайк снят.",
        examples=[True],
    )


class LikeAddDTO(BaseDTO):
    user_id: int
    post_id: int


class LikeDTO(BaseDTO):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    updated_at: datetime