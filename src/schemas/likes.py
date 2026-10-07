from src.schemas.base import BaseDTO


class LikeResponseDTO(BaseDTO):
    post_id: int
    user_id: int
