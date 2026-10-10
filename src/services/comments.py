from typing import cast

from src.schemas.comments import (
    CommentAddDTO,
    CommentCreateDTO,
    CommentDTO,
    CommentResponseDTO,
)
from src.services.base import BaseService
from src.utils.exceptions import PostNotFoundError


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
