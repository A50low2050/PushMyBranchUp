from typing import cast

from fastapi import BackgroundTasks

from src.schemas.likes import LikeAddDTO, LikeResponseDTO
from src.schemas.posts import PostDTO
from src.schemas.tokens import AccessTokenPayloadDTO
from src.schemas.users import UserDTO
from src.services.base import BaseService
from src.utils.exceptions import ObjectAlreadyExistsError, PostNotFoundError
from src.utils.notiserv import EmailMessage, NotificationService


class LikesService(BaseService):
    async def toggle_like(
        self,
        post_id: int,
        user_id: int,
        notifications: NotificationService,
        background_tasks: BackgroundTasks,
        payload: AccessTokenPayloadDTO,
    ) -> LikeResponseDTO:
        """Переключает лайк пользователя на посте:
        ставит лайк, если его нет, и убирает, если он есть."""

        post = cast(PostDTO | None, await self.db.posts.get_one_or_none(id=post_id))
        if post is None:
            raise PostNotFoundError

        like = await self.db.likes.get_one_or_none(
            user_id=user_id,
            post_id=post_id,
        )

        if like is None:
            try:
                data = LikeAddDTO(user_id=user_id, post_id=post_id)
                await self.db.likes.add(data)
                is_liked = True
            except ObjectAlreadyExistsError:
                like = await self.db.likes.get_one_or_none(
                    user_id=user_id,
                    post_id=post_id,
                )
                is_liked = like is not None
        else:
            await self.db.likes.delete(
                user_id=user_id,
                post_id=post_id,
            )
            is_liked = False

        await self.db.commit()

        like_resp = LikeResponseDTO(
            post_id=post_id,
            user_id=user_id,
            is_liked=is_liked,
        )

        if not like_resp.is_liked or post.user_id == user_id:
            return like_resp

        author = cast(
            UserDTO | None,
            await self.db.users.get_one_or_none(id=post.user_id),
        )
        if author is None:
            return like_resp

        username = payload.username
        post_snippet = (
            f"'{post.content[:25]}...'"
            if len(post.content) > 25
            else f"'{post.content}'"
        )
        subject = f"Новый лайк на вашем посте #{post.id}"
        body = (
            f"Пользователь {username} поставил лайк вашему "
            f"посту #{post.id} {post_snippet}!"
        )
        background_tasks.add_task(
            notifications.notify,
            [
                EmailMessage(
                    recipient_email=author.email,
                    subject=subject,
                    body=body,
                )
            ],
        )

        return like_resp
