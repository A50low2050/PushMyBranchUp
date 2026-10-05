from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.orm import CommonBaseORM


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
