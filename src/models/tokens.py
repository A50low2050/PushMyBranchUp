from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import CommonBaseORM


class RefreshTokenORM(CommonBaseORM):
    __tablename__ = "tokens"

    hashed_data: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    expires_at: Mapped[datetime]
    access_jti: Mapped[str]
