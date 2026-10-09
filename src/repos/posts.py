from src.models.posts import PostORM
from src.repos.base import BaseRepo
from src.schemas.posts import PostDTO


class PostsRepo(BaseRepo):
    model = PostORM
    schema = PostDTO
