from src.models.comment import CommentORM
from src.schemas.comment import CommentDTO
from src.repos.base import BaseRepo


class CommentsRepo(BaseRepo):
    model = CommentORM
    schema = CommentDTO
