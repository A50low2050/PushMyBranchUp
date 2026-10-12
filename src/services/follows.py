from src.schemas.follows import FollowResponseDTO, SubscriptionAddDTO
from src.services.base import BaseService
from src.utils.exceptions import (
    ObjectAlreadyExistsError,
    SelfFollowError,
    UserNotFoundError,
)


class FollowsService(BaseService):
    async def toggle_follow(
        self,
        followed_id: int,
        follower_id: int,
    ) -> FollowResponseDTO:
        if followed_id == follower_id:
            raise SelfFollowError

        user = await self.db.users.get_one_or_none(id=followed_id)
        if user is None:
            raise UserNotFoundError

        subscription = await self.db.subscriptions.get_one_or_none(
            follower_id=follower_id,
            followed_id=followed_id,
        )

        if subscription is None:
            try:
                data = SubscriptionAddDTO(
                    follower_id=follower_id,
                    followed_id=followed_id,
                )
                await self.db.subscriptions.add(data)
                followed = True
            except ObjectAlreadyExistsError:
                # параллельный запрос успел создать подписку раньше нас:
                # уникальный индекс отклонил вставку, состояние — "подписан"
                followed = True
        else:
            await self.db.subscriptions.delete(
                follower_id=follower_id,
                followed_id=followed_id,
            )
            followed = False

        await self.db.commit()

        return FollowResponseDTO(
            follower_id=follower_id,
            followed_id=followed_id,
            followed=followed,
        )
