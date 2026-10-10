from fastapi import APIRouter

from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.pagination import PaginationParams
from src.api.v1.errors import DBQueryHTTPError, PostNotFoundHTTPError
from src.schemas.errors import ErrorResponseDTO
from src.schemas.posts import (
    PostCreateDTO,
    PostFeedResponseDTO,
    SinglePostResponseDTO,
)
from src.services.posts import PostsService
from src.utils.exceptions import DBQueryError, PostNotFoundError

router = APIRouter(
    prefix="/posts",
    tags=["Посты"],
)


@router.post(
    "",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
    },
)
async def create_post(
    data: PostCreateDTO,
    user_id: GetSubDep,
    db: DatabaseDep,
) -> SinglePostResponseDTO:
    try:
        post = await PostsService(db).create_post(
            data=data,
            user_id=user_id,
        )
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc
    return SinglePostResponseDTO(data=post)


@router.get(
    "",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
    },
)
async def get_posts(
    pagination: PaginationParams,
    sub: GetSubDep,
    db: DatabaseDep,
) -> PostFeedResponseDTO:
    try:
        posts, total = await PostsService(db).get_posts(
            user_id=sub,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    total_pages = (total + pagination.limit - 1) // pagination.limit if total > 0 else 0
    return PostFeedResponseDTO(
        data=posts,
        total_pages=total_pages,
        per_page=pagination.limit,
        page=pagination.offset // pagination.limit + 1,
    )


@router.get(
    "/feed",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
    },
)
async def get_posts_feed(
    pagination: PaginationParams,
    sub: GetSubDep,
    db: DatabaseDep,
) -> PostFeedResponseDTO:
    try:
        posts, total = await PostsService(db).get_posts_feed(
            user_id=sub,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    total_pages = (total + pagination.limit - 1) // pagination.limit if total > 0 else 0
    return PostFeedResponseDTO(
        data=posts,
        total_pages=total_pages,
        per_page=pagination.limit,
        page=pagination.offset // pagination.limit + 1,
    )


@router.get(
    "/{post_id}",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def get_post(
    post_id: int,
    sub: GetSubDep,
    db: DatabaseDep,
) -> SinglePostResponseDTO:
    try:
        post = await PostsService(db).get_post(
            post_id=post_id,
            user_id=sub,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc
    return SinglePostResponseDTO(data=post)
