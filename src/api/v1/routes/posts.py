from fastapi import APIRouter, Query

from src.schemas.errors import ErrorResponseDTO
from src.schemas.posts import PostCreateDTO, PostResponseDTO

router = APIRouter(
    prefix="/posts",
    tags=["Посты"],
)


@router.post("", response_model=PostResponseDTO)
async def create_post(data: PostCreateDTO) -> PostResponseDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError


@router.get(
    "/user/{user_id}",
    response_model=list[PostResponseDTO],
    responses={
        404: {"model": ErrorResponseDTO},
    },
)
async def get_user_posts(
    user_id: int,
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
) -> list[PostResponseDTO]:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError


@router.get(
    "/{post_id}",
    response_model=PostResponseDTO,
    responses={
        404: {"model": ErrorResponseDTO},
    },
)
async def get_post(post_id: int) -> PostResponseDTO:
    # TODO: Add 404 error handling
    raise NotImplementedError
