from fastapi import APIRouter

from src.schemas.errors import ErrorResponseDTO
from src.schemas.likes import LikeResponseDTO

router = APIRouter(
    prefix="/posts",
    tags=["Лайки"],
)


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
