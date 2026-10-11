from fastapi import APIRouter

from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.pagination import PaginationParams
from src.api.v1.errors import (
    DBQueryHTTPError,
)
from src.schemas.errors import ErrorResponseDTO

from src.api.v1.dependencies.auth import (
    GetSubDep,
)

from src.schemas.users import (
    UserGetAllResponseDTO,
)
from src.utils.exceptions import (
    DBQueryError,
)

from src.services.users import UsersService

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get(
    "",
    responses={
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
