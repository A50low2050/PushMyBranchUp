from typing import Annotated

from fastapi import APIRouter, Body, Path, BackgroundTasks, Request, status


from src.api.v1.examples.posts import (
    CREATE_EXAMPLES,
    EDIT_EXAMPLES,
    POST_ID_EXAMPLES,
    CREATE_POST_RESPONSES,
    GET_POSTS_RESPONSES,
    GET_POSTS_FEED_RESPONSES,
    GET_POST_RESPONSES,
    EDIT_POST_RESPONSES,
    DELETE_POST_RESPONSES,
)

from src.api.v1.dependencies.auth import (
    GetAccessTokenPayloadDep,
    GetSubDep,
    GetOptionalSubDep,
)
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.notifications import NotificationsDep
from src.api.v1.dependencies.pagination import PaginationParams
from src.api.v1.errors import (
    DBQueryHTTPError,
    ForbiddenHTTPError,
    PostNotFoundHTTPError,
)
from src.config import settings
from src.schemas.posts import (
    PostCreateDTO,
    PostDeleteResponseDTO,
    PostEditDTO,
    PostFeedResponseDTO,
    SinglePostResponseDTO,
)
from src.services.posts import PostsService
from src.utils.exceptions import (
    DBQueryError,
    ForbiddenError,
    PostNotFoundError,
)
from src.utils.limiter import limiter

router = APIRouter(prefix="/posts", tags=["Посты"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Создать пост",
    description=(
        "Создаёт пост от имени авторизованного пользователя. "
        "Текст должен содержать от 1 до 2200 символов "
        "и не может состоять только из пробелов."
    ),
    responses=CREATE_POST_RESPONSES,
)
@limiter.limit(settings.rate_limit.posts_limit)
async def create_post(
    request: Request,
    data: Annotated[
        PostCreateDTO,
        Body(openapi_examples=CREATE_EXAMPLES),
    ],
    user_id: GetSubDep,
    payload: GetAccessTokenPayloadDep,
    db: DatabaseDep,
    notifications: NotificationsDep,
    background_tasks: BackgroundTasks,
) -> SinglePostResponseDTO:
    try:
        post = await PostsService(db).create_post(
            data=data,
            user_id=user_id,
            payload=payload,
            notifications=notifications,
            background_tasks=background_tasks,
        )
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return SinglePostResponseDTO(data=post)


@router.get(
    "",
    summary="Получить список постов",
    description=(
        "Публичный маршрут, авторизация не требуется. "
        "Возвращает список постов с постраничной навигацией. "
        "Количество лайков и комментариев доступно всем. "
        "Поле is_liked показывает, поставил ли текущий пользователь лайк. "
        "Для неавторизованных пользователей is_liked всегда false. "
        "Количество записей и смещение задаются параметрами пагинации."
    ),
    responses=GET_POSTS_RESPONSES,
)
@limiter.limit(settings.rate_limit.posts_limit)
async def get_posts(
    request: Request,
    pagination: PaginationParams,
    sub: GetOptionalSubDep,
    db: DatabaseDep,
) -> PostFeedResponseDTO:
    try:
        posts, total = await PostsService(db).get_posts(
            user_id=sub,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    total_pages = (total + pagination.limit - 1) // pagination.limit if total > 0 else 0

    return PostFeedResponseDTO(
        data=posts,
        total_pages=total_pages,
        per_page=pagination.limit,
        page=pagination.offset // pagination.limit + 1,
    )


@router.get(
    "/feed",
    summary="Получить ленту постов",
    description=(
        "Возвращает ленту постов для авторизованного пользователя. "
        "Результат разбит на страницы."
    ),
    responses=GET_POSTS_FEED_RESPONSES,
)
@limiter.limit(settings.rate_limit.posts_limit)
async def get_posts_feed(
    request: Request,
    pagination: PaginationParams,
    sub: GetSubDep,
    db: DatabaseDep,
) -> PostFeedResponseDTO:
    try:
        posts, total = await PostsService(db).get_posts_feed(
            user_id=sub,
            limit=pagination.limit,
            offset=pagination.offset,
        )
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    total_pages = (total + pagination.limit - 1) // pagination.limit if total > 0 else 0

    return PostFeedResponseDTO(
        data=posts,
        total_pages=total_pages,
        per_page=pagination.limit,
        page=pagination.offset // pagination.limit + 1,
    )


@router.get(
    "/{post_id}",
    summary="Получить пост",
    description=(
        "Публичный маршрут, авторизация не требуется. "
        "Возвращает пост по его ID, включая количество лайков и комментариев. "
        "Поле is_liked показывает, поставил ли текущий пользователь лайк. "
        "Для неавторизованных пользователей is_liked всегда false."
    ),
    responses=GET_POST_RESPONSES,
)
@limiter.limit(settings.rate_limit.posts_limit)
async def get_post(
    request: Request,
    post_id: Annotated[
        int,
        Path(
            description="ID поста",
            openapi_examples=POST_ID_EXAMPLES,
        ),
    ],
    sub: GetOptionalSubDep,
    db: DatabaseDep,
) -> SinglePostResponseDTO:
    try:
        post = await PostsService(db).get_post(
            post_id=post_id,
            user_id=sub,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return SinglePostResponseDTO(data=post)


@router.patch(
    "/{post_id}",
    summary="Редактировать пост",
    description=(
        "Изменяет текст существующего поста. "
        "Редактировать пост может только его автор. "
        "Новый текст должен содержать от 1 до 2200 символов "
        "и не может состоять только из пробелов."
    ),
    responses=EDIT_POST_RESPONSES,
)
@limiter.limit(settings.rate_limit.posts_limit)
async def edit_post(
    request: Request,
    post_id: Annotated[
        int,
        Path(
            description="ID редактируемого поста",
            openapi_examples=POST_ID_EXAMPLES,
        ),
    ],
    data: Annotated[
        PostEditDTO,
        Body(openapi_examples=EDIT_EXAMPLES),
    ],
    sub: GetSubDep,
    db: DatabaseDep,
) -> SinglePostResponseDTO:
    try:
        post = await PostsService(db).edit_post(
            user_id=sub,
            post_id=post_id,
            data=data,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError from exc
    except ForbiddenError as exc:
        raise ForbiddenHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return SinglePostResponseDTO(data=post)


@router.delete(
    "/{post_id}",
    summary="Удалить пост",
    description=(
        "Удаляет пост по ID. "
        "Удалить пост может только его автор. "
        "В ответе возвращается количество удалённых постов, "
        "комментариев и лайков."
    ),
    responses=DELETE_POST_RESPONSES,
)
@limiter.limit(settings.rate_limit.posts_limit)
async def delete_post(
    request: Request,
    post_id: Annotated[
        int,
        Path(
            description="ID удаляемого поста",
            openapi_examples=POST_ID_EXAMPLES,
        ),
    ],
    sub: GetSubDep,
    db: DatabaseDep,
) -> PostDeleteResponseDTO:
    try:
        result = await PostsService(db).delete_post(
            post_id=post_id,
            user_id=sub,
        )
    except PostNotFoundError as exc:
        raise PostNotFoundHTTPError from exc
    except ForbiddenError as exc:
        raise ForbiddenHTTPError from exc
    except DBQueryError as exc:
        raise DBQueryHTTPError from exc

    return PostDeleteResponseDTO(data=result)
