from src.schemas.comment import CommentCreate, CommentDTO
from src.services.base import BaseService
from src.utils.exceptions import ObjectNotFoundError


class CommentsService(BaseService):
    async def create_comment(
        self,
        *,
        post_id: int,
        token: str,
        data: CommentCreate,
    ) -> CommentDTO:
        author_id = 1

        post = await self.db.posts.get_one_or_none(id=post_id)
        if post is None:
            raise ObjectNotFoundError("Пост не найден")

        comment = await self.db.comments.create_for_post(
            post_id=post_id,
            author_id=author_id,
            data=data,
        )
        await self.db.commit()
        return comment