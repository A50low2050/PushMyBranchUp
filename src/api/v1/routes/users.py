from fastapi import APIRouter

from src.api.v1.dependencies.auth import GetSubDep
from src.schemas.errors import ErrorResponseDTO
from src.schemas.tokens import IssuedTokens
from src.schemas.users import UserLoginDTO, UserRegisterDTO, UserResponseDTO

router = APIRouter(
    prefix="/auth",
    tags=["Авторизация и аутентификация"],
)


@router.get(
    "/me",
    responses={
        401: {"model": ErrorResponseDTO},
    },
)
async def get_me(token: GetSubDep) -> dict:

    return {
        "message": "Hello, user!",
        "token": token,
    }


@router.post(
    "/register",
    response_model=UserResponseDTO,
    responses={
        409: {"model": ErrorResponseDTO},
    },
)
async def register(data: UserRegisterDTO) -> UserResponseDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError


@router.post(
    "/login",
    response_model=IssuedTokens,
    responses={
        401: {"model": ErrorResponseDTO},
    },
)
async def login(data: UserLoginDTO) -> IssuedTokens:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError
