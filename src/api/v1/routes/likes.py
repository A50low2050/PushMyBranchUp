from fastapi import APIRouter

from src.schemas.likes import LikeResponseDTO


router = APIRouter(
    prefix="/posts",
    tags=["Лайки"],
)


@router.post("/{post_id}/like", response_model=LikeResponseDTO)
async def toggle_like(post_id: int) -> LikeResponseDTO:
    ...
    
    
