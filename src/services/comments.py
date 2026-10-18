from typing import cast

from fastapi import BackgroundTasks

from src.schemas.comments import (
    CommentAddDTO,
    CommentCreateDTO,
    CommentDTO,
    CommentEditDTO,
    CommentResponseDTO,
)
from src.schemas.posts import PostDTO
from src.schemas.tokens import AccessTokenPayloadDTO
from src.schemas.users import UserDTO
from src.services.base import BaseService
from src.utils.exceptions import (
    CommentNotFoundError,
    ForbiddenError,
    ObjectNotFoundError,
    PostNotFoundError,
)
from src.utils.notiserv import EmailMessage, NotificationService


class CommentsService(BaseService):
    async def create_comment(
        self,
        post_id: int,
        user_id: int,
        data: CommentCreateDTO,
        notifications: NotificationService,
        background_tasks: BackgroundTasks,
        payload: AccessTokenPayloadDTO,
    ) -> CommentResponseDTO:
        post = cast(PostDTO | None, await self.db.posts.get_one_or_none(id=post_id))
        if post is None:
            raise PostNotFoundError

        comment_data = CommentAddDTO(
            user_id=user_id,
            post_id=post_id,
            content=data.content,
        )
        result = cast(CommentDTO, await self.db.comments.add(comment_data))
        await self.db.commit()

        comment_resp = CommentResponseDTO(
            id=result.id,
            post_id=result.post_id,
            user_id=result.user_id,
            content=result.content,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

        if post.user_id == user_id:
            return comment_resp

        author = cast(
            UserDTO | None,
            await self.db.users.get_one_or_none(id=post.user_id),
        )
        if author is None:
            return comment_resp

        username = payload.username
        post_snippet = (
            f"'{post.content[:25]}...'"
            if len(post.content) > 25
            else f"'{post.content}'"
        )
        body = (
            f"На ваш пост #{post.id} {post_snippet} оставили комментарий!\n\n"
            f"Пользователь {username} пишет:\n\n"
            f"«{result.content}»"
        )

        background_tasks.add_task(
            notifications.notify,
            [
                EmailMessage(
                    recipient_email=author.email,
                    subject=f"Новый комментарий на вашем посте #{post.id}",
                    body=body,
                )
            ],
        )

        return comment_resp

    async def get_comments(
        self,
        post_id: int,
        limit: int,
        offset: int,
    ) -> list[CommentResponseDTO]:
        if not await self.db.posts.exists(id=post_id):
            raise PostNotFoundError

        comments = await self.db.comments.get_all_filtered(
            post_id=post_id,
            limit=limit,
            offset=offset,
        )
        return [CommentResponseDTO.model_validate(c) for c in comments]

    async def get_comments_with_count(
        self,
        post_id: int,
        limit: int,
        offset: int,
    ) -> tuple[list[CommentResponseDTO], int]:
        total_count = await self.db.comments.get_total(post_id=post_id)
        if total_count == 0:
            if not await self.db.posts.exists(id=post_id):
                raise PostNotFoundError
            return [], 0

        comments = await self.db.comments.get_all_filtered(
            post_id=post_id,
            limit=limit,
            offset=offset,
        )
        return [CommentResponseDTO.model_validate(c) for c in comments], total_count

    async def get_comment(
        self,
        post_id: int,
        comment_id: int,
    ) -> CommentResponseDTO:
        try:
            comment = await self.db.comments.get_one(
                post_id=post_id,
                id=comment_id,
            )
        except ObjectNotFoundError as exc:
            raise CommentNotFoundError(str(exc)) from exc
        return CommentResponseDTO.model_validate(comment)

    async def update_comment(
        self,
        comment_id: int,
        post_id: int,
        user_id: int,
        data: CommentEditDTO,
    ) -> CommentResponseDTO:
        try:
            comment = cast(
                CommentDTO,
                await self.db.comments.get_one(
                    id=comment_id,
                    post_id=post_id,
                ),
            )
        except ObjectNotFoundError as exc:
            raise CommentNotFoundError(str(exc)) from exc

        if comment.user_id != user_id:
            raise ForbiddenError

        await self.db.comments.update(
            data=data,
            id=comment_id,
            post_id=post_id,
        )
        await self.db.commit()
        return await self.get_comment(post_id=post_id, comment_id=comment_id)

    async def delete_comment(
        self,
        comment_id: int,
        post_id: int,
        user_id: int,
    ) -> int:
        try:
            comment = cast(
                CommentDTO,
                await self.db.comments.get_one(
                    id=comment_id,
                    post_id=post_id,
                ),
            )
        except ObjectNotFoundError as exc:
            raise CommentNotFoundError(str(exc)) from exc

        if comment.user_id != user_id:
            raise ForbiddenError

        deleted_count = await self.db.comments.delete(
            id=comment_id,
            post_id=post_id,
        )
        await self.db.commit()
        return deleted_count
