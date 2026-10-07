from src.schemas.feed import FeedResponseDTO
from fastapi import APIRouter, Query

router = APIRouter(tags=["Лента"])


@router.get("/feed", response_model=FeedResponseDTO)
async def get_feed(
    limit: int = Query(20, ge=1),
    offset: int = Query(0, ge=0),
) -> FeedResponseDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError
