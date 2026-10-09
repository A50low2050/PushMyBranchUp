from src.schemas.likes import LikeAddDTO, LikeResponseDTO
from src.services.base import BaseService
from src.utils.exceptions import PostNotFoundError


class LikesService(BaseService):
    async def toggle_like(self, post_id: int, user_id: int) -> LikeResponseDTO:
        """Переключает лайк пользователя на посте:
        ставит лайк, если его нет, и убирает, если он есть."""

        post = await self.db.posts.get_one_or_none(id=post_id)
        if post is None:
            raise PostNotFoundError

        like = await self.db.likes.get_one_or_none(
            user_id=user_id,
            post_id=post_id,
        )

        if like is None:
            data = LikeAddDTO(user_id=user_id, post_id=post_id)
            await self.db.likes.add(data)
            is_liked = True
        else:
            await self.db.likes.delete(
                user_id=user_id,
                post_id=post_id,
            )
            is_liked = False

        await self.db.commit()

        return LikeResponseDTO(
            post_id=post_id,
            user_id=user_id,
            is_liked=is_liked,
        )
