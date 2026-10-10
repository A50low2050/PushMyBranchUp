from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.exc import DBAPIError, StatementError

from src.models.comments import CommentORM
from src.models.likes import LikeORM
from src.models.posts import PostORM
from src.models.subscriptions import SubscriptionORM
from src.repos.base import BaseRepo
from src.schemas.posts import PostDTO, PostResponseDTO
from src.utils.exceptions import DBQueryError, ObjectNotFoundError


class PostsRepo(BaseRepo):
    model = PostORM
    schema = PostDTO

    def _get_posts_query_with_metrics(
        self, user_id: int
    ) -> Select[tuple[PostORM, int, int, bool]]:
        likes_subq = (
            select(func.count(LikeORM.id))
            .where(LikeORM.post_id == PostORM.id)
            .scalar_subquery()
        )
        comments_subq = (
            select(func.count(CommentORM.id))
            .where(CommentORM.post_id == PostORM.id)
            .scalar_subquery()
        )
        is_liked_subq = (
            select(LikeORM.id)
            .where(LikeORM.post_id == PostORM.id, LikeORM.user_id == user_id)
            .exists()
        )

        return select(
            PostORM,
            likes_subq.label("likes_count"),
            comments_subq.label("comments_count"),
            is_liked_subq.label("is_liked"),
        )

    @staticmethod
    def _row_to_dto(row: Any) -> PostResponseDTO:
        post: PostORM = row[0]
        likes_count: int = row[1]
        comments_count: int = row[2]
        is_liked: bool = row[3]
        return PostResponseDTO(
            post_id=post.id,
            user_id=post.user_id,
            content=post.content,
            created_at=post.created_at,
            updated_at=post.updated_at,
            likes_count=likes_count or 0,
            comments_count=comments_count or 0,
            is_liked=bool(is_liked),
        )

    async def get_total(self) -> int:
        query = select(func.count(PostORM.id)).select_from(PostORM)
        try:
            result = await self.session.execute(query)
            total = result.scalar()
            return total or 0
        except (StatementError, DBAPIError) as exc:
            raise DBQueryError from exc

    async def get_total_feed(self, user_id: int) -> int:
        query = (
            select(func.count(PostORM.id))
            .join(SubscriptionORM, PostORM.user_id == SubscriptionORM.followed_id)
            .where(SubscriptionORM.follower_id == user_id)
        )
        try:
            result = await self.session.execute(query)
            total = result.scalar()
            return total or 0
        except (StatementError, DBAPIError) as exc:
            raise DBQueryError from exc

    async def get_posts_with_rel(
        self,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[PostResponseDTO]:
        query = self._get_posts_query_with_metrics(user_id).order_by(
            PostORM.created_at.desc(),
            PostORM.id.desc(),
        )

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        try:
            results = await self.session.execute(query)
        except (StatementError, DBAPIError) as exc:
            raise DBQueryError from exc

        return [self._row_to_dto(row) for row in results.all()]

    async def get_post_with_rel(self, post_id: int, user_id: int) -> PostResponseDTO:
        query = self._get_posts_query_with_metrics(user_id).where(PostORM.id == post_id)
        try:
            result = await self.session.execute(query)
            row = result.one_or_none()
        except (StatementError, OverflowError, DBAPIError) as exc:
            raise DBQueryError from exc

        if row is None:
            raise ObjectNotFoundError

        return self._row_to_dto(row)

    async def get_posts_feed(
        self,
        user_id: int,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[PostResponseDTO]:
        query = (
            self._get_posts_query_with_metrics(user_id)
            .join(SubscriptionORM, PostORM.user_id == SubscriptionORM.followed_id)
            .where(SubscriptionORM.follower_id == user_id)
            .order_by(PostORM.created_at.desc(), PostORM.id.desc())
        )

        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        try:
            results = await self.session.execute(query)
        except (StatementError, DBAPIError) as exc:
            raise DBQueryError from exc

        return [self._row_to_dto(row) for row in results.all()]
