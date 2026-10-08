from sqlalchemy import insert

from src.models.comment import CommentORM
from src.repos.base import BaseRepo
from src.schemas.comment import CommentCreate, CommentDTO


class CommentsRepo(BaseRepo):
    model = CommentORM
    schema = CommentDTO

    async def create_for_post(
        self,
        *,
        post_id: int,
        author_id: int,
        data: CommentCreate,
    ) -> CommentDTO:
        stmt = (
            insert(self.model)
            .values(post_id=post_id, author_id=author_id, text=data.text)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        obj = result.scalars().one()
        return self.schema.model_validate(obj)
