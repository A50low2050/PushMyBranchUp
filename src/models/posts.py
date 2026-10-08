from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import CommonBaseORM

if TYPE_CHECKING:
    from src.models.users import UserORM
    from src.models.comments import CommentORM
    from src.models.likes import LikeORM


class PostORM(CommonBaseORM):
    __tablename__ = "posts"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["UserORM"] = relationship(
        back_populates="posts",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    comments: Mapped[list["CommentORM"]] = relationship(
        back_populates="post",
    )
    likes: Mapped[list["LikeORM"]] = relationship(
        back_populates="post",
    )
