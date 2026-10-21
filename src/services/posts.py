from typing import cast

from fastapi import BackgroundTasks

from src.schemas.posts import (
    PostAddDTO,
    PostCreateDTO,
    PostDeleteResultDTO,
    PostDTO,
    PostEditDTO,
    PostResponseDTO,
)
from src.schemas.tokens import AccessTokenPayloadDTO
from src.services.base import BaseService
from src.utils.exceptions import (
    ForbiddenError,
    ObjectNotFoundError,
    PostNotFoundError,
)
from src.utils.logserv import LogService
from src.utils.notiserv import EmailMessage, NotificationService

logger = LogService.get_logger(__name__)


class PostsService(BaseService):
    async def create_post(
        self,
        data: PostCreateDTO,
        user_id: int,
        notifications: NotificationService,
        background_tasks: BackgroundTasks,
        payload: AccessTokenPayloadDTO,
    ) -> PostResponseDTO:
        post = PostAddDTO(
            user_id=user_id,
            content=data.content,
        )

        result = cast(PostDTO, await self.db.posts.add(post))
        await self.db.commit()

        post_resp = PostResponseDTO(
            post_id=result.id,
            user_id=result.user_id,
            content=result.content,
            created_at=result.created_at,
            updated_at=result.updated_at,
            likes_count=0,
            comments_count=0,
            is_liked=False,
        )

        follower_emails = await self.db.subscriptions.get_follower_emails(
            followed_id=user_id
        )
        if not follower_emails:
            return post_resp

        subject = f"Новая публикация от {payload.email}"
        post_snippet = (
            f"«{post_resp.content[:100]}...»"
            if len(post_resp.content) > 100
            else f"«{post_resp.content}»"
        )
        body = (
            f"Пользователь {payload.email}, на которого вы подписаны, "
            f"опубликовал новый пост #{post_resp.post_id}:\n\n"
            f"{post_snippet}"
        )

        background_tasks.add_task(
            notifications.notify,
            [
                EmailMessage(
                    recipient_email=email,
                    subject=subject,
                    body=body,
                )
                for email in follower_emails
            ],
        )

        return post_resp

    async def get_posts(
        self,
        user_id: int | None,
        limit: int,
        offset: int,
    ) -> tuple[list[PostResponseDTO], int]:
        posts = await self.db.posts.get_posts_with_rel(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        total = await self.db.posts.get_total()
        return posts, total

    async def get_post(self, post_id: int, user_id: int | None) -> PostResponseDTO:
        try:
            post = await self.db.posts.get_post_with_rel(
                post_id=post_id,
                user_id=user_id,
            )
        except ObjectNotFoundError as exc:
            logger.error("Получение поста: пост #%s не найден", post_id)
            raise PostNotFoundError from exc
        return post

    async def get_posts_feed(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> tuple[list[PostResponseDTO], int]:
        posts = await self.db.posts.get_posts_feed(
            user_id=user_id,
            limit=limit,
            offset=offset,
        )
        total = await self.db.posts.get_total_feed(
            user_id=user_id,
        )
        return posts, total

    async def delete_post(self, post_id: int, user_id: int) -> PostDeleteResultDTO:
        deleted_count = await self.db.posts.delete(id=post_id, user_id=user_id)
        if not deleted_count:
            if not await self.db.posts.exists(id=post_id):
                logger.error("Удаление поста: пост #%s не найден", post_id)
                raise PostNotFoundError
            logger.error(
                "Удаление поста: пользователь #%s не является автором поста #%s",
                user_id,
                post_id,
            )
            raise ForbiddenError

        await self.db.commit()
        return PostDeleteResultDTO(post_id=post_id, deleted=True)

    async def edit_post(
        self,
        user_id: int,
        post_id: int,
        data: PostEditDTO,
    ) -> PostResponseDTO:
        try:
            post = cast(PostDTO, await self.db.posts.get_one(id=post_id))
        except ObjectNotFoundError as exc:
            logger.error("Редактирование поста: пост #%s не найден", post_id)
            raise PostNotFoundError(str(exc)) from exc

        if post.user_id != user_id:
            logger.error(
                "Редактирование поста: пользователь #%s не является "
                "автором поста #%s",
                user_id,
                post_id,
            )
            raise ForbiddenError

        await self.db.posts.update(data=data, id=post_id)
        await self.db.commit()
        return await self.get_post(post_id=post_id, user_id=user_id)
