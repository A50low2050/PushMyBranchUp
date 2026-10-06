from fastapi import APIRouter

from src.api.v1.dependencies.auth import GetTokenDep
from src.api.v1.errors import UnauthorizedHTTPError

from src.schemas.users import UserLoginDTO, UserRegisterDTO, UserResponseDTO, TokenDTO


router = APIRouter(
    prefix="/auth",
    tags=["Авторизация и аутентификация"],
)


@router.get("/me")
async def get_me(token: GetTokenDep) -> dict[str, str]:
    if not token:
        raise UnauthorizedHTTPError

    return {
        "message": "Hello, user!",
        "token": token,
    }


@router.post("/register", response_model=UserResponseDTO)
async def register(data: UserRegisterDTO) -> UserResponseDTO:
    ...