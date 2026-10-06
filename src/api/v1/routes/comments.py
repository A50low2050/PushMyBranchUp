from fastapi import APIRouter

from src.schemas.comments import CommentCreateDTO, CommentResponseDTO


router = APIRouter(
    prefix="/posts",
    tags=["Комментарии"],
)


@router.post("/{post_id}/comments", response_model=CommentResponseDTO)
async def create_comment(
    post_id: int,
    data: CommentCreateDTO,
) -> CommentResponseDTO:
    ...
    
@router.get("/{post_id}/comments", response_model=list[CommentResponseDTO])
async def get_comments(
    post_id: int,
    limit: int = 20,
    offset: int = 0,
) -> list[CommentResponseDTO]:
    ...