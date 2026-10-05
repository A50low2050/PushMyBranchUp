from datetime import datetime

from sqlalchemy import (
    DateTime,
    Integer,
    func,
)
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class BaseORM(AsyncAttrs, DeclarativeBase): ...


class CommonBaseORM(BaseORM):
    """Базовая модель для всех ORM моделей, содержит общие поля"""

    __abstract__ = True

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, sort_order=-1
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now,
        server_default=func.now(),
        onupdate=func.now(),
    )
