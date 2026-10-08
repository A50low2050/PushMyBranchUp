from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import CommonBaseORM

if TYPE_CHECKING:
    from src.models.users import UserORM
    from src.models.posts import PostORM


class LikeORM(CommonBaseORM):
    __tablename__ = "likes"
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "post_id",
            name="uq_likes_user_post",
        ),
    )
    user: Mapped["UserORM"] = relationship(
        back_populates="likes",
    )
    post: Mapped["PostORM"] = relationship(
        back_populates="likes",
    )
