from fastapi import APIRouter

from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.errors import BadRequestHTTPError, UserNotFoundHTTPError
from src.schemas.errors import ErrorResponseDTO
from src.schemas.follows import FollowResponseDTO
from src.services.follows import FollowsService
from src.utils.exceptions import SelfFollowError, UserNotFoundError

router = APIRouter(
    prefix="/users",
    tags=["Подписки"],
)


@router.put(
    "/{user_id}/follow",
    response_model=FollowResponseDTO,
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def toggle_follow(
    user_id: int,
    sub: GetSubDep,
    db: DatabaseDep,
) -> FollowResponseDTO:
    try:
        result = await FollowsService(db).toggle_follow(
            followed_id=user_id,
            follower_id=sub,
        )
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc
    except SelfFollowError as exc:
        raise BadRequestHTTPError from exc

    return result


@router.post(
    "/{user_id}/follow",
    response_model=FollowResponseDTO,
    responses={
        400: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
        409: {"model": ErrorResponseDTO},
    },
)
async def follow_user(user_id: int) -> FollowResponseDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError


@router.delete(
    "/{user_id}/follow",
    response_model=FollowResponseDTO,
    responses={
        404: {"model": ErrorResponseDTO},
        409: {"model": ErrorResponseDTO},
    },
)
async def unfollow_user(user_id: int) -> FollowResponseDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError
