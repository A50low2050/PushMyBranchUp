from src.models.comments import CommentORM
from src.repos.base import BaseRepo
from src.schemas.comments import CommentDTO


class CommentsRepo(BaseRepo):
    model = CommentORM
    schema = CommentDTO
