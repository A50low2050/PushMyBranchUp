from typing import cast

from src.schemas.posts import (
    PostAddDTO,
    PostCreateDTO,
    PostDTO,
    PostResponseDTO,
)
from src.services.base import BaseService
from src.utils.exceptions import ObjectNotFoundError, PostNotFoundError


class PostsService(BaseService):
    async def create_post(
        self,
        data: PostCreateDTO,
        user_id: int,
    ) -> PostResponseDTO:
        post = PostAddDTO(
            user_id=user_id,
            content=data.content,
        )

        result = cast(PostDTO, await self.db.posts.add(post))
        await self.db.commit()

        return PostResponseDTO(
            post_id=result.id,
            user_id=result.user_id,
            content=result.content,
            created_at=result.created_at,
            updated_at=result.updated_at,
            likes_count=0,
            comments_count=0,
            is_liked=False,
        )

    async def get_posts(
        self,
        user_id: int,
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

    async def get_post(self, post_id: int, user_id: int) -> PostResponseDTO:
        try:
            post = await self.db.posts.get_post_with_rel(
                post_id=post_id,
                user_id=user_id,
            )
        except ObjectNotFoundError as exc:
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
