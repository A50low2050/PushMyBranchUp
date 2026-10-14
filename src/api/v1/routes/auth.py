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
    summary="Получить свой профиль",
    description="Возвращает данные авторизованного пользователя. Требуется access-токен.",
    responses={
        200: {
            "description": "Данные пользователя получены",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "id": 1,
                            "username": "alex",
                            "email": "alex@example.com",
                            "created_at": "2026-10-13T12:00:00",
                            "updated_at": "2026-10-13T12:00:00",
                        }
                    }
                }
            },
        },
        401: {
            "model": ErrorResponseDTO,
            "description": "Пользователь не авторизован",
            "content": {
                "application/json": {
                    "example": {
                        "error": "UNAUTHORIZED",
                        "message": "Пользователь не авторизован",
                    }
                }
            },
        },
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
    summary="Зарегистрировать пользователя",
    description=(
        "Создаёт нового пользователя по имени, электронной почте и паролю.\n\n"
        "Авторизация не требуется.\n\n"
        "**Требования:** имя — от 3 до 255 символов, "
        "пароль — от 8 до 128 символов, email — корректного формата."
    ),
    responses={
        200: {
            "description": "Пользователь успешно зарегистрирован",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "id": 1,
                            "username": "alex",
                            "email": "alex@example.com",
                            "created_at": "2026-10-13T12:00:00",
                            "updated_at": "2026-10-13T12:00:00",
                        }
                    }
                }
            },
        },
        400: {
            "model": ErrorResponseDTO,
            "description": "Ошибка запроса к базе данных",
            "content": {
                "application/json": {
                    "example": {
                        "error": "DB_QUERY_ERROR",
                        "message": "Ошибка запроса к базе данных",
                    }
                }
            },
        },
        409: {
            "model": ErrorResponseDTO,
            "description": "Пользователь с такими данными уже существует",
        },
        422: {
            "model": ErrorResponseDTO,
            "description": "Ошибка валидации данных регистрации",
            "content": {
                "application/json": {
                    "example": {
                        "error": "VALIDATION_ERROR",
                        "message": "Invalid request data",
                    }
                }
            },
        },
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
    summary="Войти в аккаунт",
    description=(
        "Авторизует пользователя по электронной почте и паролю.\n\n"
        "Авторизация не требуется.\n\n"
        "При успешном входе возвращает access-токен и refresh-токен. "
        "Refresh-токен также сохраняется в HttpOnly cookie.\n\n"
        "Для выполнения защищённых запросов скопируйте `access_token` "
        "и используйте кнопку **Authorize** в Swagger."
    ),
    responses={
        200: {
            "description": "Вход выполнен успешно",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "example.access.token",
                        "refresh_token": "example.refresh.token",
                        "type": "Bearer",
                    }
                }
            },
        },
        400: {
            "model": ErrorResponseDTO,
            "description": "Ошибка запроса к базе данных",
            "content": {
                "application/json": {
                    "example": {
                        "error": "DB_QUERY_ERROR",
                        "message": "Ошибка запроса к базе данных",
                    }
                }
            },
        },
        401: {
            "model": ErrorResponseDTO,
            "description": "Неверная электронная почта или пароль",
        },
        422: {
            "model": ErrorResponseDTO,
            "description": "Некорректные данные для входа",
            "content": {
                "application/json": {
                    "example": {
                        "error": "VALIDATION_ERROR",
                        "message": "Invalid request data",
                    }
                }
            },
        },
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
    summary="Обновить токены авторизации",
    description=(
        "Выдаёт новую пару access-токена и refresh-токена.\n\n"
        "Refresh-токен берётся из HttpOnly cookie, "
        "которая сохраняется при входе в аккаунт.\n\n"
        "**Тело запроса не требуется.**\n\n"
        "После успешного обновления новый refresh-токен "
        "сохраняется в cookie, а новый access-токен "
        "можно использовать для авторизации запросов."
    ),
    responses={
        200: {
            "description": "Токены успешно обновлены",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "new.example.access.token",
                        "refresh_token": "new.example.refresh.token",
                        "type": "Bearer",
                    }
                }
            },
        },
        400: {
            "model": ErrorResponseDTO,
            "description": "Ошибка запроса к базе данных",
            "content": {
                "application/json": {
                    "example": {
                        "error": "DB_QUERY_ERROR",
                        "message": "Ошибка запроса к базе данных",
                    }
                }
            },
        },
        401: {
            "model": ErrorResponseDTO,
            "description": "Refresh-токен отсутствует, недействителен или истёк",
        },
        404: {
            "model": ErrorResponseDTO,
            "description": "Пользователь не найден",
        },
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
    summary="Выйти из аккаунта",
    description=(
        "Завершает текущую сессию пользователя.\n\n"
        "Для выхода необходимы действующий access-токен "
        "и refresh-токен в HttpOnly cookie.\n\n"
        "При успешном выходе refresh-токен удаляется из cookie.\n\n"
        "**Тело запроса не требуется.**"
    ),
    responses={
        204: {
            "description": "Выход выполнен успешно. Тело ответа отсутствует.",
        },
        400: {
            "model": ErrorResponseDTO,
            "description": "Ошибка запроса к базе данных",
            "content": {
                "application/json": {
                    "example": {
                        "error": "DB_QUERY_ERROR",
                        "message": "Ошибка запроса к базе данных",
                    }
                }
            },
        },
        401: {
            "model": ErrorResponseDTO,
            "description": "Пользователь не авторизован или токен недействителен",
        },
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
    summary="Изменить имя пользователя",
    description=(
        "Изменяет имя текущего авторизованного пользователя.\n\n"
        "Требуется действующий access-токен.\n\n"
        "**Требования:** новое имя должно содержать от 3 до 255 символов.\n\n"
        "После успешного изменения возвращает обновлённые данные профиля."
    ),
    responses={
        200: {
            "description": "Имя пользователя успешно изменено",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "id": 1,
                            "username": "alex_new",
                            "email": "alex@example.com",
                            "created_at": "2026-10-13T12:00:00",
                            "updated_at": "2026-10-13T13:00:00",
                        }
                    }
                }
            },
        },
        400: {
            "model": ErrorResponseDTO,
            "description": "Ошибка запроса к базе данных",
            "content": {
                "application/json": {
                    "example": {
                        "error": "DB_QUERY_ERROR",
                        "message": "Ошибка запроса к базе данных",
                    }
                }
            },
        },
        401: {
            "model": ErrorResponseDTO,
            "description": "Пользователь не авторизован",
        },
        404: {
            "model": ErrorResponseDTO,
            "description": "Пользователь не найден",
        },
        409: {
            "model": ErrorResponseDTO,
            "description": "Имя пользователя уже занято",
        },
        422: {
            "model": ErrorResponseDTO,
            "description": "Некорректное имя пользователя",
            "content": {
                "application/json": {
                    "example": {
                        "error": "VALIDATION_ERROR",
                        "message": "Invalid request data",
                    }
                }
            },
        },
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
