from src.models.subscriptions import SubscriptionORM
from src.repos.base import BaseRepo
from src.schemas.follows import SubscriptionDTO


class SubscriptionsRepo(BaseRepo):
    model = SubscriptionORM
    schema = SubscriptionDTO
