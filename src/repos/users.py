from sqlalchemy import func, select
from sqlalchemy.exc import DBAPIError, StatementError

from src.models.users import UserORM
from src.repos.base import BaseRepo
from src.schemas.users import UserDTO
from src.utils.exceptions import DBQueryError


class UsersRepo(BaseRepo):
    model = UserORM
    schema = UserDTO

    async def get_total(self) -> int:
        query = select(func.count(UserORM.id)).select_from(UserORM)
        try:
            result = await self.session.execute(query)
            total = result.scalar()
            return total or 0
        except (StatementError, DBAPIError) as exc:
            raise DBQueryError from exc
