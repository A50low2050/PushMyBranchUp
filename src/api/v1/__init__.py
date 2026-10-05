from fastapi import APIRouter

from src.api.v1.routes.users import router as auth_router

router = APIRouter(
    prefix="/v1",
)
router.include_router(auth_router)
