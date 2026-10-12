from fastapi import APIRouter, Response

from src.api.v1.dependencies.auth import (
    GetRefreshTokenDep,
    GetSubDep,
)
from src.api.v1.dependencies.cache import CacheDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.errors import (
    DBQueryHTTPError,
    InvalidLoginDataHTTPError,
    UserAlreadyExistsHTTPError,
    UserNotFoundHTTPError,
)
from src.config import settings
from src.schemas.errors import ErrorResponseDTO
from src.schemas.tokens import IssuedTokens
from src.schemas.users import (
    UserGetMeResponseDTO,
    UserLoginDTO,
    UserRegisterDTO,
    UserUpdateDTO,
)
from src.services.users import UsersService
from src.utils.exceptions import (
    DBQueryError,
    InvalidLoginDataError,
    UserAlreadyExistsError,
    UserNotFoundError,
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
async def get_me(
    sub: GetSubDep,
    db: DatabaseDep,
) -> UserGetMeResponseDTO:
    try:
        user = await UsersService(db).get_user(user_id=sub)
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return UserGetMeResponseDTO(data=user)


@router.post(
    "/register",
    responses={
        400: {"model": ErrorResponseDTO},
        409: {"model": ErrorResponseDTO},
    },
)
async def register(
    data: UserRegisterDTO,
    db: DatabaseDep,
) -> UserGetMeResponseDTO:
    try:
        user = await UsersService(db).register(data=data)
    except UserAlreadyExistsError as exc:
        raise UserAlreadyExistsHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return UserGetMeResponseDTO(data=user)


@router.post(
    "/login",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
    },
)
async def login(
    data: UserLoginDTO,
    response: Response,
    db: DatabaseDep,
    cache: CacheDep,
) -> IssuedTokens:
    try:
        tokens = await UsersService(db).login(
            data=data,
            cache=cache,
        )
    except InvalidLoginDataError as exc:
        raise InvalidLoginDataHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    response.set_cookie(
        key=settings.auth.refresh_token_cookie_name,
        value=tokens.refresh_token,
        httponly=True,
    )
    return tokens


@router.post(
    "/refresh",
    responses={
        400: {"model": ErrorResponseDTO},
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
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc
    except InvalidLoginDataError as exc:
        raise InvalidLoginDataHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    response.set_cookie(
        key=settings.auth.refresh_token_cookie_name,
        value=tokens.refresh_token,
        httponly=True,
    )
    return tokens


@router.post(
    "/logout",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
    },
    status_code=204,
)
async def logout(
    response: Response,
    sub: GetSubDep,
    rf_token: GetRefreshTokenDep,
    cache: CacheDep,
    db: DatabaseDep,
) -> None:
    try:
        await UsersService(db).logout(
            rf_token=rf_token,
            user_id=sub,
            cache=cache,
        )
    except InvalidLoginDataError as exc:
        raise InvalidLoginDataHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    response.delete_cookie(settings.auth.refresh_token_cookie_name)


@router.patch(
    "/me",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
        409: {"model": ErrorResponseDTO},
    },
)
async def update_me(
    data: UserUpdateDTO,
    sub: GetSubDep,
    db: DatabaseDep,
) -> UserGetMeResponseDTO:
    try:
        user = await UsersService(db).update_user(
            user_id=sub,
            data=data,
        )
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc
    except UserAlreadyExistsError as exc:
        raise UserAlreadyExistsHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return UserGetMeResponseDTO(data=user)
