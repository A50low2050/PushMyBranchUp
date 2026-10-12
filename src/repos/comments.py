from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, StatementError

from src.models.comments import CommentORM
from src.repos.base import BaseRepo
from src.schemas.comments import CommentDTO
from src.utils.exceptions import DBQueryError


class CommentsRepo(BaseRepo):
    model = CommentORM
    schema = CommentDTO

    async def get_total(self) -> int:
        query = select(func.count(CommentORM.id)).select_from(CommentORM)
        try:
            result = await self.session.execute(query)
            total = result.scalar()
            return total or 0
        except (StatementError, DBAPIError) as exc:
            raise DBQueryError from exc
