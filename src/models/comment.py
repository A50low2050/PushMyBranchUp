from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import CommonBaseORM

if TYPE_CHECKING:
    from src.models.users import UserORM
    from src.models.posts import PostORM


class CommentORM(CommonBaseORM):
    __tablename__ = "comments"
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id"),
        nullable=False,
    )
    author: Mapped["UserORM"] = relationship(
        back_populates="comments",
    )
    post: Mapped["PostORM"] = relationship(
        back_populates="comments",
    )
