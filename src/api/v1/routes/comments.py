from fastapi import APIRouter, Query, status

from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.errors import DBQueryHTTPError, PostNotFoundHTTPError
from src.schemas.comments import CommentCreateDTO, CommentResponseDTO
from src.schemas.errors import ErrorResponseDTO
from src.services.comments import CommentsService
from src.utils.exceptions import DBQueryError, PostNotFoundError

router = APIRouter(
    prefix="/posts",
    tags=["Комментарии"],
)


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def create_comment(
    post_id: int,
    data: CommentCreateDTO,
    sub: GetSubDep,
    db: DatabaseDep,
) -> CommentResponseDTO:
    try:
        result = await CommentsService(db).create_comment(
            post_id=post_id,
            user_id=sub,
            data=data,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return result


@router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponseDTO],
    responses={
        400: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def get_comments(
    post_id: int,
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
) -> list[CommentResponseDTO]:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError
