from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, StatementError

from src.models.subscriptions import SubscriptionORM
from src.models.users import UserORM
from src.repos.base import BaseRepo
from src.schemas.follows import SubscriptionDTO
from src.utils.exceptions import DBQueryError


class SubscriptionsRepo(BaseRepo):
    model = SubscriptionORM
    schema = SubscriptionDTO

    async def get_follower_emails(self, followed_id: int) -> list[str]:
        """Возвращает email-ы всех подписчиков пользователя followed_id."""
        query = (
            select(UserORM.email)
            .join(SubscriptionORM, UserORM.id == SubscriptionORM.follower_id)
            .where(SubscriptionORM.followed_id == followed_id)
        )
        try:
            result = await self.session.execute(query)
            return list(result.scalars().all())
        except (StatementError, DBAPIError) as exc:
            raise DBQueryError from exc
