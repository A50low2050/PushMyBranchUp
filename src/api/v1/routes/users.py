from fastapi import APIRouter, Response

from src.api.v1.dependencies.cache import CacheDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.errors import (
    InvalidLoginDataHTTPError,
    UserAlreadyExistsHTTPError,
    UserNotFoundHTTPError,
)
from src.schemas.errors import ErrorResponseDTO
from src.schemas.tokens import IssuedTokens

from src.api.v1.dependencies.auth import (
    GetAccessTokenPayloadDep,
    GetRefreshTokenDep,
    GetSubDep,
)

from src.schemas.users import (
    UserLoginDTO,
    UserRegisterDTO,
    UserUpdateDTO,
)
from src.utils.exceptions import (
    InvalidLoginDataError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

from src.services.users import UsersService
from src.config import settings

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
async def get_me(sub: GetSubDep, db: DatabaseDep) -> dict:
    try:
        user = await UsersService(db).get_user(user_id=sub)
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc

    return {
        "data": user,
    }


@router.post(
    "/register",
    responses={
        409: {"model": ErrorResponseDTO},
    },
)
async def register(data: UserRegisterDTO, db: DatabaseDep) -> dict:
    try:
        user = await UsersService(db).register(data=data)
    except UserAlreadyExistsError as exc:
        raise UserAlreadyExistsHTTPError from exc

    return {
        "data": user,
    }


@router.post(
    "/login",
    responses={
        401: {"model": ErrorResponseDTO},
    },
)
async def login(
    data: UserLoginDTO, response: Response, db: DatabaseDep
) -> IssuedTokens:
    try:
        tokens = await UsersService(db).login(data=data)
    except InvalidLoginDataError as exc:
        raise InvalidLoginDataHTTPError from exc

    response.set_cookie(
        key=settings.auth.refresh_token_cookie_name,
        value=tokens.refresh_token,
        httponly=True,
    )
    return tokens


@router.post(
    "/refresh",
    responses={
        401: {"model": ErrorResponseDTO},
    },
)
async def refresh_token(
    token: GetRefreshTokenDep,
    response: Response,
    db: DatabaseDep,
    cache: CacheDep,
) -> IssuedTokens:

    try:
        tokens = await UsersService(db).refresh(
            token=token,
            cache=cache,
        )
    except InvalidLoginDataError as exc:
        raise InvalidLoginDataHTTPError from exc

    response.set_cookie(
        key=settings.auth.refresh_token_cookie_name,
        value=tokens.refresh_token,
        httponly=True,
    )
    return tokens


@router.post(
    "/logout",
    responses={
        401: {"model": ErrorResponseDTO},
    },
    status_code=204,
)
async def logout(
    response: Response,
    token: GetAccessTokenPayloadDep,
    cache: CacheDep,
    db: DatabaseDep,
) -> None:
    try:
        await UsersService(db).logout(
            access_t=token,
            cache=cache,
        )
    except InvalidLoginDataError as exc:
        raise InvalidLoginDataHTTPError from exc

    response.delete_cookie(settings.auth.refresh_token_cookie_name)


@router.patch(
    "/me",
    responses={
        401: {"model": ErrorResponseDTO},
        409: {"model": ErrorResponseDTO},
    },
)
async def update_me(
    data: UserUpdateDTO,
    sub: GetSubDep,
    db: DatabaseDep,
) -> dict:
    try:
        updated_count = await UsersService(db).update_user(
            user_id=sub,
            data=data,
        )
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc

    return {
        "data": {
            "updated": updated_count,
        }
    }
