from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import CommonBaseORM

if TYPE_CHECKING:
    from src.models.users import UserORM


class SubscriptionORM(CommonBaseORM):
    __tablename__ = "subscriptions"
    __table_args__ = (
        UniqueConstraint(
            "follower_id",
            "followed_id",
            name="uq_subscriptions_follower_followed",
        ),
    )
    follower_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    followed_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )
    follower: Mapped["UserORM"] = relationship(
        foreign_keys=[follower_id],
        back_populates="outgoing_subscriptions",
    )

    followed: Mapped["UserORM"] = relationship(
        foreign_keys=[followed_id],
        back_populates="incoming_subscriptions",
    )
