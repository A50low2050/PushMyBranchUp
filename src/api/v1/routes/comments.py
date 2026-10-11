from fastapi import APIRouter, status

from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.pagination import Pagination
from src.api.v1.errors import (
    CommentNotFoundHTTPError,
    DBQueryHTTPError,
    PostNotFoundHTTPError,
)
from src.schemas.comments import CommentCreateDTO, CommentResponseDTO
from src.schemas.errors import ErrorResponseDTO
from src.services.comments import CommentsService
from src.utils.exceptions import CommentNotFoundError, DBQueryError, PostNotFoundError

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
    pagination: Pagination,
    db: DatabaseDep,
) -> list[CommentResponseDTO]:
    try:
        comments = await CommentsService(db).get_comments(
            post_id=post_id,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError(str(exc)) from exc
    return comments


@router.get(
    "/{post_id}/comments/{comment_id}",
    response_model=list[CommentResponseDTO],
    responses={
        400: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def get_comment(
    post_id: int,
    comment_id: int,
    db: DatabaseDep,
) -> CommentResponseDTO:
    try:
        comment = await CommentsService(db).get_comment(
            post_id=post_id,
            comment_id=comment_id,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError(str(exc)) from exc
    except CommentNotFoundError as exc:
        raise CommentNotFoundHTTPError(str(exc)) from exc
    return comment


@router.delete(
    "/posts/{post_id}/comments/{comment_id}",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    sub: GetSubDep,
    db: DatabaseDep,
) -> dict:
    try:
        deleted_comments = await CommentsService(db).delete_comment(
            post_id=post_id,
            comment_id=comment_id,
            user_id=sub,
        )
    except CommentNotFoundError as exc:
        raise CommentNotFoundHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return {"data": {"deleted_count": deleted_comments}}
