from fastapi import APIRouter

from src.schemas.posts import PostCreateDTO, PostResponseDTO


router = APIRouter(
    prefix="/posts",
    tags=["Посты"],
)


@router.post("", response_model=PostResponseDTO)
async def create_post(data: PostCreateDTO) -> PostResponseDTO:
    ...
    
    
@router.get("/{post_id}", response_model=PostResponseDTO)
async def get_post(post_id: int) -> PostResponseDTO:
    ...
    
    
@router.get("/user/{user_id}", response_model=list[PostResponseDTO])
async def get_user_posts(
    user_id: int,
    limit: int = 20,
    offset: int = 0,
) -> list[PostResponseDTO]:
    ...