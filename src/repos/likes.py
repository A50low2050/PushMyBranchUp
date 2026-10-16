from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, StatementError

from src.models.likes import LikeORM
from src.repos.base import BaseRepo
from src.schemas.likes import LikeDTO
from src.utils.exceptions import DBQueryError


class LikesRepo(BaseRepo):
    model = LikeORM
    schema = LikeDTO

    async def get_total(self, post_id: int) -> int:
        query = (
            select(func.count(LikeORM.id))
            .select_from(LikeORM)
            .filter(LikeORM.post_id == post_id)
        )
        try:
            result = await self.session.execute(query)
            total = result.scalar()
            return total or 0
        except (StatementError, DBAPIError) as exc:
            raise DBQueryError from exc
