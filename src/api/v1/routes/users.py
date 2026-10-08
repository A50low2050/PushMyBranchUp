from fastapi import APIRouter

from src.api.v1.dependencies.auth import GetTokenDep
from src.api.v1.errors import UnauthorizedHTTPError
from src.schemas.errors import ErrorResponseDTO

from src.schemas.users import (
    RefreshTokenRequestDTO,
    TokenDTO,
    UserLoginDTO,
    UserRegisterDTO,
    UserResponseDTO,
    UserUpdateDTO,
)

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
async def get_me(token: GetTokenDep) -> dict[str, str]:
    if not token:
        raise UnauthorizedHTTPError

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
    response_model=TokenDTO,
    responses={
        401: {"model": ErrorResponseDTO},
    },
)
async def login(data: UserLoginDTO) -> TokenDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError


@router.post(
    "/refresh",
    response_model=TokenDTO,
    responses={
        401: {"model": ErrorResponseDTO},
    },
)
async def refresh_token(data: RefreshTokenRequestDTO) -> TokenDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError


@router.post(
    "/logout",
    responses={
        401: {"model": ErrorResponseDTO},
    },
    status_code=204,
)
async def logout(token: GetTokenDep) -> None:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError


@router.patch(
    "/me",
    response_model=UserResponseDTO,
    responses={
        401: {"model": ErrorResponseDTO},
        409: {"model": ErrorResponseDTO},
    },
)
async def update_me(data: UserUpdateDTO, token: GetTokenDep) -> UserResponseDTO:
    # TODO: Implement after the service layer is ready
    raise NotImplementedError
