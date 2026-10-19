from typing import cast

from fastapi import BackgroundTasks

from src.schemas.follows import FollowResponseDTO, SubscriptionAddDTO
from src.schemas.tokens import AccessTokenPayloadDTO
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
        payload: AccessTokenPayloadDTO,
    ) -> FollowResponseDTO:
        if followed_id == follower_id:
            raise SelfFollowError

        followed_user = cast(
            UserDTO | None, await self.db.users.get_one_or_none(id=followed_id)
        )
        if followed_user is None:
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

        follower_name = payload.username

        background_tasks.add_task(
            notifications.notify,
            [
                EmailMessage(
                    recipient_email=followed_user.email,
                    subject=f"Новый подписчик: {follower_name}",
                    body=f"На вас подписался пользователь {follower_name}.",
                )
            ],
        )

        return follow_resp
