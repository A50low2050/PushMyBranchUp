from src.schemas.posts import PostAddDTO, PostCreateDTO, PostResponseDTO
from src.services.base import BaseService
from typing import cast
from src.schemas.posts import PostDTO


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
            id=result.id,
            user_id=result.user_id,
            content=result.content,
            created_at=result.created_at,
            likes_count=0,
            comments_count=0,
            is_liked=False,
        )