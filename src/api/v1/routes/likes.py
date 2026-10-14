from fastapi import APIRouter, BackgroundTasks

from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.notifications import NotificationsDep
from src.api.v1.errors import DBQueryHTTPError, PostNotFoundHTTPError
from src.schemas.errors import ErrorResponseDTO
from src.schemas.likes import LikeResponseDTO
from src.services.likes import LikesService
from src.utils.exceptions import DBQueryError, PostNotFoundError

router = APIRouter(
    prefix="/posts",
    tags=["Лайки"],
)


@router.put(
    "/{post_id}/like",
    summary="Поставить или убрать лайк",
    description=(
        "Переключает состояние лайка на указанном посте.\n\n"
        "**Требуется авторизация** через access-токен.\n\n"
        "**Как работает:**\n"
        "- Если пользователь ещё не лайкнул пост — лайк добавляется.\n"
        "- Если пользователь уже лайкнул пост — лайк удаляется.\n\n"
        "**Параметры:**\n"
        "- `post_id` — ID поста, которому нужно поставить "
        "или с которого нужно убрать лайк.\n\n"
        "**Тело запроса не требуется.**\n\n"
        "ID пользователя определяется автоматически по access-токену.\n\n"
        "**Ограничения:**\n"
        "- Указанный пост должен существовать.\n"
        "- Для установки и удаления лайка используется один метод PUT.\n\n"
        "В ответе возвращается текущее состояние лайка."
    ),
    response_model=LikeResponseDTO,
    responses={
        200: {
            "description": "Состояние лайка успешно изменено",
            "content": {
                "application/json": {
                    "examples": {
                        "liked": {
                            "summary": "Лайк поставлен",
                            "value": {
                                "post_id": 1,
                                "user_id": 2,
                                "is_liked": True,
                            },
                        },
                        "unliked": {
                            "summary": "Лайк снят",
                            "value": {
                                "post_id": 1,
                                "user_id": 2,
                                "is_liked": False,
                            },
                        },
                    }
                }
            },
        },
        400: {
            "model": ErrorResponseDTO,
            "description": "Ошибка запроса к базе данных",
        },
        401: {
            "model": ErrorResponseDTO,
            "description": "Пользователь не авторизован",
        },
        404: {
            "model": ErrorResponseDTO,
            "description": "Пост с указанным ID не найден",
        },
        422: {
            "model": ErrorResponseDTO,
            "description": "Некорректный ID поста",
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
async def toggle_like(
    post_id: int,
    sub: GetSubDep,
    db: DatabaseDep,
    notifications: NotificationsDep,
    background_tasks: BackgroundTasks,
) -> LikeResponseDTO:
    try:
        result = await LikesService(db).toggle_like(
            post_id=post_id,
            user_id=sub,
            notifications=notifications,
            background_tasks=background_tasks,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return result