from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import CommonBaseORM

if TYPE_CHECKING:
    from src.models.posts import PostORM
    from src.models.comments import CommentORM
    from src.models.likes import LikeORM
    from src.models.subscriptions import SubscriptionORM


class UserORM(CommonBaseORM):
    __tablename__ = "users"
    username: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    posts: Mapped[list["PostORM"]] = relationship(
        back_populates="author",
    )
    comments: Mapped[list["CommentORM"]] = relationship(
        back_populates="author",
    )
    likes: Mapped[list["LikeORM"]] = relationship(
        back_populates="user",
    )
    outgoing_subscriptions: Mapped[list["SubscriptionORM"]] = relationship(
        foreign_keys="SubscriptionORM.follower_id",
        back_populates="follower",
    )

    incoming_subscriptions: Mapped[list["SubscriptionORM"]] = relationship(
        foreign_keys="SubscriptionORM.followed_id",
        back_populates="followed",
    )
