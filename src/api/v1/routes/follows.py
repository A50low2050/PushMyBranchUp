from fastapi import APIRouter

from src.schemas.errors import ErrorResponseDTO
from src.schemas.follows import FollowResponseDTO

router = APIRouter(
    prefix="/users",
    tags=["Подписки"],
)


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
