from src.models.likes import LikeORM
from src.repos.base import BaseRepo
from src.schemas.likes import LikeDTO


class LikesRepo(BaseRepo):
    model = LikeORM
    schema = LikeDTO
