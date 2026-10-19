from fastapi import APIRouter, BackgroundTasks, status

from src.api.v1.examples.comments import (
    CREATE_COMMENT_RESPONSES,
    DELETE_COMMENT_RESPONSES,
    GET_COMMENT_RESPONSES,
    GET_COMMENTS_RESPONSES,
    UPDATE_COMMENT_RESPONSES,
)
from src.api.v1.dependencies.auth import GetAccessTokenPayloadDep, GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.notifications import NotificationsDep
from src.api.v1.dependencies.pagination import PaginationParams
from src.api.v1.errors import (
    CommentNotFoundHTTPError,
    DBQueryHTTPError,
    ForbiddenHTTPError,
    PostNotFoundHTTPError,
)
from src.schemas.comments import (
    CommentCreateDTO,
    CommentDeleteDataDTO,
    CommentDeleteResponseDTO,
    CommentEditDTO,
    CommentFeedResponseDTO,
    CommentResponseDTO,
)
from src.services.comments import CommentsService
from src.utils.exceptions import (
    CommentNotFoundError,
    DBQueryError,
    ForbiddenError,
    PostNotFoundError,
)

router = APIRouter(
    prefix="/posts",
    tags=["Комментарии"],
)


@router.post(
    "/{post_id}/comments",
    summary="Создать комментарий",
    description=(
        "Добавляет новый комментарий к указанному посту.\n\n"
        "**Требуется авторизация** через access-токен.\n\n"
        "**Параметры:**\n"
        "- `post_id` — ID поста, к которому добавляется комментарий.\n"
        "- `content` — текст комментария от 1 до 2200 символов.\n\n"
        "Комментарий не может состоять только из пробелов.\n\n"
        "ID автора определяется автоматически по access-токену."
    ),
    response_model=CommentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    responses=CREATE_COMMENT_RESPONSES,
)
async def create_comment(
    post_id: int,
    data: CommentCreateDTO,
    sub: GetSubDep,
    payload: GetAccessTokenPayloadDep,
    db: DatabaseDep,
    notifications: NotificationsDep,
    background_tasks: BackgroundTasks,
) -> CommentResponseDTO:
    try:
        result = await CommentsService(db).create_comment(
            post_id=post_id,
            user_id=sub,
            payload=payload,
            data=data,
            notifications=notifications,
            background_tasks=background_tasks,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return result


@router.get(
    "/{post_id}/comments",
    summary="Получить комментарии поста",
    description=(
        "Возвращает список комментариев указанного поста с пагинацией.\n\n"
        "**Авторизация не требуется.**\n\n"
        "**Параметры:**\n"
        "- `post_id` — ID поста.\n"
        "- `limit` — количество комментариев на странице (от 1 до 15, по умолчанию 5).\n"
        "- `offset` — количество пропускаемых комментариев (по умолчанию 0).\n\n"
        "**Пример:** `limit=5&offset=10` — получить третью страницу "
        "при размере страницы 5 комментариев.\n\n"
        "**Ответ содержит:**\n"
        "- `page` — номер текущей страницы.\n"
        "- `per_page` — количество комментариев на странице.\n"
        "- `total_pages` — общее количество страниц.\n"
        "- `data` — массив комментариев.\n\n"
        "Если комментариев нет, возвращается пустой массив `data`."
    ),
    response_model=CommentFeedResponseDTO,
    responses=GET_COMMENTS_RESPONSES,
)
async def get_comments(
    post_id: int,
    pagination: PaginationParams,
    _: GetSubDep,
    db: DatabaseDep,
) -> CommentFeedResponseDTO:
    try:
        comments, total_count = await CommentsService(db).get_comments_with_count(
            post_id=post_id,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError(str(exc)) from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    total_pages = (
        (total_count + pagination.limit - 1) // pagination.limit
        if total_count > 0
        else 0
    )
    return CommentFeedResponseDTO(
        data=comments,
        page=pagination.offset // pagination.limit + 1,
        per_page=pagination.limit,
        total_pages=total_pages,
    )


@router.get(
    "/{post_id}/comments/{comment_id}",
    summary="Получить комментарий по ID",
    description=(
        "Возвращает информацию об одном комментарии указанного поста.\n\n"
        "**Авторизация не требуется.**\n\n"
        "**Параметры:**\n"
        "- `post_id` — ID поста.\n"
        "- `comment_id` — ID комментария.\n\n"
        "В ответе возвращаются текст комментария, "
        "ID автора, ID поста и даты создания и изменения."
    ),
    response_model=CommentResponseDTO,
    responses=GET_COMMENT_RESPONSES,
)
async def get_comment(
    post_id: int,
    comment_id: int,
    _: GetSubDep,
    db: DatabaseDep,
) -> CommentResponseDTO:
    try:
        comment = await CommentsService(db).get_comment(
            post_id=post_id,
            comment_id=comment_id,
        )
    except CommentNotFoundError as exc:
        raise CommentNotFoundHTTPError(str(exc)) from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc
    return comment


@router.patch(
    "/{post_id}/comments/{comment_id}",
    summary="Редактировать комментарий",
    description=(
        "Изменяет текст существующего комментария.\n\n"
        "**Требуется авторизация** через access-токен.\n\n"
        "**Редактировать комментарий может только его автор.**\n\n"
        "**Параметры:**\n"
        "- `post_id` — ID поста.\n"
        "- `comment_id` — ID редактируемого комментария.\n"
        "- `content` — новый текст комментария от 1 до 2200 символов.\n\n"
        "Комментарий не может состоять только из пробелов.\n\n"
        "После успешного изменения возвращаются обновлённые данные комментария."
    ),
    response_model=CommentResponseDTO,
    responses=UPDATE_COMMENT_RESPONSES,
)
async def update_comment(
    post_id: int,
    comment_id: int,
    data: CommentEditDTO,
    sub: GetSubDep,
    db: DatabaseDep,
) -> CommentResponseDTO:
    try:
        result = await CommentsService(db).update_comment(
            post_id=post_id,
            comment_id=comment_id,
            user_id=sub,
            data=data,
        )
    except CommentNotFoundError as exc:
        raise CommentNotFoundHTTPError(str(exc)) from exc
    except ForbiddenError as exc:
        raise ForbiddenHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return result


@router.delete(
    "/{post_id}/comments/{comment_id}",
    summary="Удалить комментарий",
    description=(
        "Удаляет комментарий из указанного поста.\n\n"
        "**Требуется авторизация** через access-токен.\n\n"
        "**Удалить комментарий может только его автор.**\n\n"
        "**Параметры:**\n"
        "- `post_id` — ID поста.\n"
        "- `comment_id` — ID удаляемого комментария.\n\n"
        "**Тело запроса не требуется.**\n\n"
        "После успешного удаления возвращается количество удалённых комментариев "
        "в поле `data.deleted_count`."
    ),
    response_model=CommentDeleteResponseDTO,
    responses=DELETE_COMMENT_RESPONSES,
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    sub: GetSubDep,
    db: DatabaseDep,
) -> CommentDeleteResponseDTO:
    try:
        deleted_comments = await CommentsService(db).delete_comment(
            post_id=post_id,
            comment_id=comment_id,
            user_id=sub,
        )
    except CommentNotFoundError as exc:
        raise CommentNotFoundHTTPError from exc
    except ForbiddenError as exc:
        raise ForbiddenHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return CommentDeleteResponseDTO(
        data=CommentDeleteDataDTO(deleted_count=deleted_comments)
    )
