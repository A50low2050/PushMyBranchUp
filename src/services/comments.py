from typing import cast

from src.schemas.comments import (
    CommentAddDTO,
    CommentCreateDTO,
    CommentDTO,
    CommentEditDTO,
    CommentResponseDTO,
)
from src.services.base import BaseService
from src.utils.exceptions import (
    CommentNotFoundError,
    ObjectNotFoundError,
    PostNotFoundError,
)


class CommentsService(BaseService):
    async def create_comment(
        self,
        post_id: int,
        user_id: int,
        data: CommentCreateDTO,
    ) -> CommentResponseDTO:
        post = await self.db.posts.get_one_or_none(id=post_id)
        if post is None:
            raise PostNotFoundError

        comment_data = CommentAddDTO(
            user_id=user_id,
            post_id=post_id,
            content=data.content,
        )
        result = cast(CommentDTO, await self.db.comments.add(comment_data))
        await self.db.commit()

        return CommentResponseDTO(
            id=result.id,
            post_id=result.post_id,
            user_id=result.user_id,
            content=result.content,
            created_at=result.created_at,
            updated_at=result.updated_at,
        )

    async def get_comments(
        self, post_id: int, limit: int, offset: int
    ) -> list[CommentResponseDTO]:
        post = await self.db.posts.get_one_or_none(id=post_id)
        if post is None:
            raise PostNotFoundError

        comments: list[CommentResponseDTO] = await self.db.comments.get_all_filtered(
            post_id=post_id,
            limit=limit,
            offset=offset,
        )  # type: ignore
        return comments

    async def get_comment(
        self,
        post_id: int,
        comment_id: int,
    ) -> CommentResponseDTO:
        try:
            comment: CommentResponseDTO = await self.db.comments.get_one(
                post_id=post_id,
                id=comment_id,
            )  # type: ignore
        except ObjectNotFoundError as exc:
            raise CommentNotFoundError(str(exc)) from exc
        return comment

    async def update_comment(
        self,
        comment_id: int,
        post_id: int,
        user_id: int,
        data: CommentEditDTO,
    ) -> int:
        try:
            await self.db.comments.get_one(
                id=comment_id,
                user_id=user_id,
                post_id=post_id,
            )
        except ObjectNotFoundError as exc:
            raise PostNotFoundError(str(exc)) from exc

        updated_count = await self.db.posts.update(data=data)
        await self.db.commit()
        return updated_count

    async def delete_comment(
        self,
        comment_id: int,
        post_id: int,
        user_id: int,
    ) -> int:
        try:
            await self.db.comments.get_one(
                id=comment_id,
                user_id=user_id,
                post_id=post_id,
            )
        except ObjectNotFoundError as exc:
            raise CommentNotFoundError(str(exc)) from exc

        deleted_count = await self.db.comments.delete(
            id=comment_id,
            post_id=post_id,
        )
        await self.db.commit()
        return deleted_count
