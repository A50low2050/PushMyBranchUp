from fastapi import APIRouter, BackgroundTasks

from src.api.v1.examples.follows import TOGGLE_FOLLOW_RESPONSES
from src.api.v1.dependencies.auth import GetAccessTokenPayloadDep, GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.notifications import NotificationsDep
from src.api.v1.errors import BadRequestHTTPError, UserNotFoundHTTPError
from src.schemas.follows import FollowResponseDTO
from src.services.follows import FollowsService
from src.utils.exceptions import SelfFollowError, UserNotFoundError

router = APIRouter(
    prefix="/users",
    tags=["Подписки"],
)


@router.put(
    "/{user_id}/follow",
    summary="Подписаться или отписаться от пользователя",
    description=(
        "Переключает состояние подписки на указанного пользователя.\n\n"
        "**Требуется авторизация** через access-токен.\n\n"
        "**Как работает:**\n"
        "- Если вы ещё не подписаны на пользователя — создаётся подписка.\n"
        "- Если вы уже подписаны — подписка отменяется.\n\n"
        "**Параметры:**\n"
        "- `user_id` — ID пользователя, на которого нужно подписаться "
        "или от которого нужно отписаться.\n\n"
        "**Тело запроса не требуется.**\n\n"
        "ID текущего пользователя определяется автоматически по access-токену.\n\n"
        "**Ограничения:**\n"
        "- Нельзя подписаться на самого себя.\n"
        "- Указанный пользователь должен существовать.\n\n"
        "Для подписки и отписки используется один и тот же метод PUT."
    ),
    response_model=FollowResponseDTO,
    responses=TOGGLE_FOLLOW_RESPONSES,
)
async def toggle_follow(
    user_id: int,
    sub: GetSubDep,
    payload: GetAccessTokenPayloadDep,
    db: DatabaseDep,
    notifications: NotificationsDep,
    background_tasks: BackgroundTasks,
) -> FollowResponseDTO:
    try:
        result = await FollowsService(db).toggle_follow(
            followed_id=user_id,
            follower_id=sub,
            payload=payload,
            notifications=notifications,
            background_tasks=background_tasks,
        )
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc
    except SelfFollowError as exc:
        raise BadRequestHTTPError from exc

    return result
