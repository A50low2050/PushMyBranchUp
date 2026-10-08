from typing import Annotated

from fastapi import Depends

from src.api.v1.dependencies.db import DatabaseDep
from src.services.comment import CommentsService


def get_comments_service(db: DatabaseDep) -> CommentsService:
    return CommentsService(db)


GetCommentsServiceDep = Annotated[CommentsService, Depends(get_comments_service)]
