from fastapi import APIRouter

from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.pagination import PaginationParams
from src.api.v1.errors import (
    DBQueryHTTPError,
    UserNotFoundHTTPError,
)
from src.schemas.errors import ErrorResponseDTO
from src.schemas.users import (
    UserGetAllResponseDTO,
    UserSingleResponseDTO,
)
from src.services.users import UsersService
from src.utils.exceptions import (
    DBQueryError,
    UserNotFoundError,
)

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get(
    "",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
    },
)
async def get_users(
    _: GetSubDep,
    pagination: PaginationParams,
    db: DatabaseDep,
) -> UserGetAllResponseDTO:
    try:
        users = await UsersService(db).get_users(
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return UserGetAllResponseDTO(data=users)


@router.get(
    "/{user_id}",
    responses={
        400: {"model": ErrorResponseDTO},
        401: {"model": ErrorResponseDTO},
        404: {"model": ErrorResponseDTO},
    },
)
async def get_user(
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
