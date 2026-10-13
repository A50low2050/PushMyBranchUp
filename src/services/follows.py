from typing import cast

from fastapi import BackgroundTasks

from src.schemas.follows import FollowResponseDTO, SubscriptionAddDTO
from src.schemas.users import UserDTO
from src.services.base import BaseService
from src.utils.exceptions import (
    ObjectAlreadyExistsError,
    SelfFollowError,
    UserNotFoundError,
)
from src.utils.notiserv import EmailMessage, NotificationService


class FollowsService(BaseService):
    async def toggle_follow(
        self,
        followed_id: int,
        follower_id: int,
        notifications: NotificationService,
        background_tasks: BackgroundTasks,
    ) -> FollowResponseDTO:
        if followed_id == follower_id:
            raise SelfFollowError

        user = cast(UserDTO | None, await self.db.users.get_one_or_none(id=followed_id))
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

        follow_resp = FollowResponseDTO(
            follower_id=follower_id,
            followed_id=followed_id,
            followed=followed,
        )

        if not follow_resp.followed:
            return follow_resp

        background_tasks.add_task(
            notifications.notify,
            [
                EmailMessage(
                    recipient_email=user.email,
                    subject="Новый подписчик",
                    body="На вас подписался новый пользователь.",
                )
            ],
        )

        return follow_resp
