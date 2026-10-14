from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: int = Field(
        5,
        ge=1,
        le=15,
        title="Количество записей",
        description="Сколько записей вернуть за один запрос (от 1 до 15).",
        examples=[5, 10, 15],
    )

    offset: int = Field(
        0,
        ge=0,
        title="Смещение",
        description="Сколько записей пропустить от начала списка. Например, 5 — пропустить первые пять.",
        examples=[0, 5, 10],
    )


PaginationParams = Annotated[Pagination, Depends(Pagination)]
