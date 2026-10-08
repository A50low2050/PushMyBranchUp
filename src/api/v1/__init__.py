from fastapi import APIRouter

from src.api.v1.routes.users import router as auth_router
from src.api.v1.routes.comments import router as comments_router
from src.api.v1.routes.follows import router as follows_router
from src.api.v1.routes.likes import router as likes_router
from src.api.v1.routes.posts import router as posts_router
from src.api.v1.routes.feed import router as feed_router

router = APIRouter(
    prefix="/v1",
)
router.include_router(auth_router)
router.include_router(posts_router)
router.include_router(comments_router)
router.include_router(likes_router)
router.include_router(follows_router)
router.include_router(feed_router)
