from fastapi import APIRouter, status

from src.api.v1.dependencies.auth import GetTokenDep
from src.schemas.comment import CommentCreate, CommentDTO
from src.api.v1.dependencies.services import GetCommentsServiceDep

router = APIRouter(
    prefix="/posts",
    tags=["Комментарии"],
)


@router.post(
    "/{post_id}/comments",
    response_model=CommentDTO,
    status_code=status.HTTP_201_CREATED,
)
async def create_comment(
    post_id: int,
    data: CommentCreate,
    token: GetTokenDep,
    service: GetCommentsServiceDep,
) -> CommentDTO:
    return await service.create_comment(
        post_id=post_id,
        token=token,
        data=data,
    )
