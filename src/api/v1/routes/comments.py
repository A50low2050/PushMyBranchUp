from fastapi import APIRouter, status

from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.pagination import PaginationParams
from src.api.v1.errors import (
    CommentNotFoundHTTPError,
    DBQueryHTTPError,
    ForbiddenHTTPError,
    PostNotFoundHTTPError,
)
from src.schemas.comments import (
    CommentCreateDTO,
    CommentDeleteDataDTO,
    CommentDeleteResponseDTO,
    CommentEditDTO,
    CommentFeedResponseDTO,
    SingleCommentResponseDTO,
    CommentResponseDTO,
)
from src.schemas.errors import ErrorResponseDTO
from src.services.comments import CommentsService
from src.utils.exceptions import (
    CommentNotFoundError,
    DBQueryError,
    ForbiddenError,
    PostNotFoundError,
)

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
    response_model=CommentFeedResponseDTO,
    responses={
        400: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def get_comments(
    post_id: int,
    pagination: PaginationParams,
    db: DatabaseDep,
) -> CommentFeedResponseDTO:
    try:
        comments, total_count = await CommentsService(db).get_comments_with_count(
            post_id=post_id,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError(str(exc)) from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    total_pages = (
        (total_count + pagination.limit - 1) // pagination.limit
        if total_count > 0
        else 0
    )
    return CommentFeedResponseDTO(
        data=comments,
        page=pagination.offset // pagination.limit + 1,
        per_page=pagination.limit,
        total_pages=total_pages,
    )


@router.get(
    "/{post_id}/comments/{comment_id}",
    response_model=CommentResponseDTO,
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
    except CommentNotFoundError as exc:
        raise CommentNotFoundHTTPError(str(exc)) from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc
    return comment


@router.patch(
    "/{post_id}/comments/{comment_id}",
    response_model=CommentResponseDTO,
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
        403: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def update_comment(
    post_id: int,
    comment_id: int,
    data: CommentEditDTO,
    sub: GetSubDep,
    db: DatabaseDep,
) -> CommentResponseDTO:
    try:
        result = await CommentsService(db).update_comment(
            post_id=post_id,
            comment_id=comment_id,
            user_id=sub,
            data=data,
        )
    except CommentNotFoundError as exc:
        raise CommentNotFoundHTTPError(str(exc)) from exc
    except ForbiddenError as exc:
        raise ForbiddenHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return result


@router.delete(
    "/{post_id}/comments/{comment_id}",
    response_model=CommentDeleteResponseDTO,
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
        403: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    sub: GetSubDep,
    db: DatabaseDep,
) -> CommentDeleteResponseDTO:
    try:
        deleted_comments = await CommentsService(db).delete_comment(
            post_id=post_id,
            comment_id=comment_id,
            user_id=sub,
        )
    except CommentNotFoundError as exc:
        raise CommentNotFoundHTTPError from exc
    except ForbiddenError as exc:
        raise ForbiddenHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return CommentDeleteResponseDTO(
        data=CommentDeleteDataDTO(deleted_count=deleted_comments)
    )
