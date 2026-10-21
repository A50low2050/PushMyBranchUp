from fastapi import APIRouter, Request

from src.api.v1.examples.users import (
    GET_USER_RESPONSES,
    GET_USERS_RESPONSES,
)
from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.pagination import PaginationParams
from src.api.v1.errors import (
    DBQueryHTTPError,
    UserNotFoundHTTPError,
)
from src.config import settings
from src.schemas.users import (
    UserGetAllResponseDTO,
    UserSingleResponseDTO,
)
from src.services.users import UsersService
from src.utils.exceptions import (
    DBQueryError,
    UserNotFoundError,
)
from src.utils.limiter import limiter

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get(
    "",
    summary="Получить список пользователей",
    description=(
        "Возвращает список зарегистрированных пользователей с пагинацией.\n\n"
        "**Требуется авторизация** через access-токен.\n\n"
        "**Параметры:**\n"
        "- `limit` — количество пользователей на странице "
        "(от 1 до 15, по умолчанию 5).\n"
        "- `offset` — количество пропускаемых пользователей "
        "(по умолчанию 0).\n\n"
        "**Пример:** `limit=5&offset=10` — получить третью страницу "
        "при размере страницы 5 пользователей.\n\n"
        "**Ответ содержит:**\n"
        "- `page` — номер текущей страницы.\n"
        "- `per_page` — количество пользователей на странице.\n"
        "- `total_pages` — общее количество страниц.\n"
        "- `data` — массив пользователей.\n\n"
        "Если пользователей нет, возвращается пустой массив `data`."
    ),
    response_model=UserGetAllResponseDTO,
    responses=GET_USERS_RESPONSES,
)
@limiter.limit(settings.rate_limit.users_limit)
async def get_users(
    request: Request,
    _: GetSubDep,
    pagination: PaginationParams,
    db: DatabaseDep,
) -> UserGetAllResponseDTO:
    try:
        users, total_count = await UsersService(db).get_users_with_count(
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    total_pages = (
        (total_count + pagination.limit - 1) // pagination.limit
        if total_count > 0
        else 0
    )
    return UserGetAllResponseDTO(
        data=users,
        page=pagination.offset // pagination.limit + 1,
        per_page=pagination.limit,
        total_pages=total_pages,
    )


@router.get(
    "/{user_id}",
    summary="Получить пользователя по ID",
    description=(
        "Возвращает информацию об указанном пользователе.\n\n"
        "**Требуется авторизация** через access-токен.\n\n"
        "**Параметры:**\n"
        "- `user_id` — уникальный ID пользователя.\n\n"
        "**Ответ содержит:**\n"
        "- `id` — ID пользователя.\n"
        "- `username` — имя пользователя.\n"
        "- `email` — электронная почта.\n"
        "- `created_at` — дата регистрации.\n"
        "- `updated_at` — дата последнего изменения профиля.\n\n"
        "Данные пользователя возвращаются внутри объекта `data`."
    ),
    response_model=UserSingleResponseDTO,
    responses=GET_USER_RESPONSES,
)
@limiter.limit(settings.rate_limit.users_limit)
async def get_user(
    request: Request,
    user_id: int,
    _: GetSubDep,
    db: DatabaseDep,
) -> UserSingleResponseDTO:
    try:
        user = await UsersService(db).get_user(user_id=user_id)
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return UserSingleResponseDTO(data=user)
