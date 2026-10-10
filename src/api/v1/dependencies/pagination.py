from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field


class Pagination(BaseModel):
    limit: int = Field(
        5,
        ge=1,
        le=15,
        title="Количество постов",
        description="Количество постов на странице",
    )

    offset: int = Field(
        0,
        ge=0,
        title="Смещение",
        description="Смещение от начала списка",
    )


PaginationParams = Annotated[Pagination, Depends(Pagination)]
