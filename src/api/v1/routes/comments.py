from fastapi import APIRouter, Query

from src.schemas.comments import CommentCreateDTO, CommentResponseDTO
from src.schemas.errors import ErrorResponseDTO

router = APIRouter(
    prefix="/posts",
    tags=["Комментарии"],
)


@router.post(
    "/{post_id}/comments",
    response_model=CommentResponseDTO,
    responses={
        404: {"model": ErrorResponseDTO},
    },
)
async def create_comment(
    post_id: int,
    data: CommentCreateDTO,
) -> CommentResponseDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError


@router.get(
    "/{post_id}/comments",
    response_model=list[CommentResponseDTO],
    responses={
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
