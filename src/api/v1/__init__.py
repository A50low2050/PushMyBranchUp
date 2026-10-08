from fastapi import APIRouter

from src.api.v1.routes.users import router as auth_router
from src.api.v1.routes.comments import router as comments_router

router = APIRouter(
    prefix="/v1",
)
router.include_router(auth_router)
router.include_router(comments_router)
