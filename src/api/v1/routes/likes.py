from fastapi import APIRouter

from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.errors import DBQueryHTTPError, PostNotFoundHTTPError
from src.schemas.errors import ErrorResponseDTO
from src.schemas.likes import LikeResponseDTO
from src.services.likes import LikesService
from src.utils.exceptions import DBQueryError, PostNotFoundError

router = APIRouter(
    prefix="/posts",
    tags=["Лайки"],
)


@router.put(
    "/{post_id}/like",
    response_model=LikeResponseDTO,
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def toggle_like(
    post_id: int,
    sub: GetSubDep,
    db: DatabaseDep,
) -> LikeResponseDTO:
    try:
        result = await LikesService(db).toggle_like(
            post_id=post_id,
            user_id=sub,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return result


@router.post(
    "/{post_id}/like",
    response_model=LikeResponseDTO,
    responses={
        404: {"model": ErrorResponseDTO},
        409: {"model": ErrorResponseDTO},
    },
)
async def add_like(post_id: int) -> LikeResponseDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError


@router.delete(
    "/{post_id}/like",
    response_model=LikeResponseDTO,
    responses={
        404: {"model": ErrorResponseDTO},
        409: {"model": ErrorResponseDTO},
    },
)
async def delete_like(post_id: int) -> LikeResponseDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError
