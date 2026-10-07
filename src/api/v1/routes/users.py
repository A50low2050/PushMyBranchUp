from fastapi import APIRouter

from src.api.v1.dependencies.auth import GetSubDep

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация и аутентификация"],
)


@router.get("/me")
async def get_me(sub: GetSubDep) -> dict:

    return {
        "message": "Hello, user!",
        "token": sub,
    }
