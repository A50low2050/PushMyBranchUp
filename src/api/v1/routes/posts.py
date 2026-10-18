from typing import Annotated

from fastapi import APIRouter, Body, Path, BackgroundTasks


from src.api.v1.dependencies.auth import GetSubDep
from src.api.v1.dependencies.db import DatabaseDep
from src.api.v1.dependencies.notifications import NotificationsDep
from src.api.v1.dependencies.pagination import PaginationParams
from src.api.v1.errors import (
    DBQueryHTTPError,
    ForbiddenHTTPError,
    PostNotFoundHTTPError,
)
from src.schemas.errors import ErrorResponseDTO
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

router = APIRouter(prefix="/posts", tags=["Посты"])


# Примеры для Swagger. На работу API не влияют.

POST_EXAMPLE = {
    "post_id": 1,
    "user_id": 1,
    "content": "Мой первый пост!",
    "likes_count": 0,
    "is_liked": False,
    "comments_count": 0,
    "created_at": "2026-10-13T12:00:00",
    "updated_at": "2026-10-13T12:00:00",
}

SINGLE_POST_EXAMPLE = {
    "data": POST_EXAMPLE,
}

POST_FEED_EXAMPLE = {
    "page": 1,
    "per_page": 10,
    "total_pages": 1,
    "data": [POST_EXAMPLE],
}

DELETE_EXAMPLE = {
    "data": {
        "post_id": 1,
        "deleted": True,
    }
}

POST_ID_EXAMPLES = {
    "existing": {
        "summary": "Существующий пост",
        "description": "Пример ID поста. Замените на существующий ID.",
        "value": 1,
    },
    "missing": {
        "summary": "Несуществующий пост",
        "description": "Пример ID для проверки ошибки 404.",
        "value": 999999,
    },
}

CREATE_EXAMPLES = {
    "valid": {
        "summary": "Обычный пост",
        "value": {"content": "Сегодня начал работать над новым проектом!"},
    },
    "short": {
        "summary": "Короткий пост",
        "value": {"content": "Привет!"},
    },
    "empty": {
        "summary": "Ошибка: пустой текст",
        "description": "Вызовет ошибку валидации 422.",
        "value": {"content": ""},
    },
    "spaces": {
        "summary": "Ошибка: только пробелы",
        "description": "Вызовет ошибку валидации 422.",
        "value": {"content": "   "},
    },
    "missing": {
        "summary": "Ошибка: отсутствует content",
        "description": "Вызовет ошибку валидации 422.",
        "value": {},
    },
}

EDIT_EXAMPLES = {
    "valid": {
        "summary": "Изменить текст",
        "value": {"content": "Обновлённый текст поста."},
    },
    "empty": {
        "summary": "Ошибка: пустой текст",
        "value": {"content": ""},
    },
    "spaces": {
        "summary": "Ошибка: только пробелы",
        "value": {"content": "   "},
    },
}


def error_response(
    description: str,
    error: str,
    message: str,
) -> dict:
    """Документация ошибки для Swagger."""
    return {
        "model": ErrorResponseDTO,
        "description": description,
        "content": {
            "application/json": {
                "example": {
                    "error": error,
                    "message": message,
                }
            }
        },
    }


BAD_REQUEST_RESPONSE = error_response(
    "Ошибка запроса к базе данных",
    "DB_QUERY_ERROR",
    "Ошибка запроса к базе данных",
)

UNAUTHORIZED_RESPONSE = error_response(
    "Необходим действительный access-токен",
    "UNAUTHORIZED",
    "Пользователь не авторизован",
)

FORBIDDEN_RESPONSE = error_response(
    "Недостаточно прав для выполнения действия",
    "FORBIDDEN",
    "Доступ запрещен",
)

NOT_FOUND_RESPONSE = error_response(
    "Пост не найден",
    "POST_NOT_FOUND",
    "Пост не найден",
)

VALIDATION_RESPONSE = error_response(
    "Некорректные данные запроса",
    "VALIDATION_ERROR",
    "Invalid request data",
)


@router.post(
    "",
    summary="Создать пост",
    description=(
        "Создаёт пост от имени авторизованного пользователя. "
        "Текст должен содержать от 1 до 2200 символов "
        "и не может состоять только из пробелов."
    ),
    responses={
        200: {
            "description": "Пост создан",
            "content": {"application/json": {"example": SINGLE_POST_EXAMPLE}},
        },
        400: BAD_REQUEST_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_RESPONSE,
    },
)
async def create_post(
    data: Annotated[
        PostCreateDTO,
        Body(openapi_examples=CREATE_EXAMPLES),
    ],
    user_id: GetSubDep,
    db: DatabaseDep,
    notifications: NotificationsDep,
    background_tasks: BackgroundTasks,
) -> SinglePostResponseDTO:
    try:
        post = await PostsService(db).create_post(
            data=data,
            user_id=user_id,
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
        "Возвращает список постов с постраничной навигацией. "
        "Количество записей и смещение задаются параметрами "
        "пагинации."
    ),
    responses={
        200: {
            "description": "Список постов получен",
            "content": {
                "application/json": {
                    "examples": {
                        "with_posts": {
                            "summary": "Список с постами",
                            "value": POST_FEED_EXAMPLE,
                        },
                        "empty": {
                            "summary": "Пустой список",
                            "value": {
                                "page": 1,
                                "per_page": 10,
                                "total_pages": 0,
                                "data": [],
                            },
                        },
                    }
                }
            },
        },
        400: BAD_REQUEST_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_RESPONSE,
    },
)
async def get_posts(
    pagination: PaginationParams,
    sub: GetSubDep,
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
    responses={
        200: {
            "description": "Лента получена",
            "content": {
                "application/json": {
                    "examples": {
                        "with_posts": {
                            "summary": "Лента с постами",
                            "value": POST_FEED_EXAMPLE,
                        },
                        "empty": {
                            "summary": "Пустая лента",
                            "value": {
                                "page": 1,
                                "per_page": 10,
                                "total_pages": 0,
                                "data": [],
                            },
                        },
                    }
                }
            },
        },
        400: BAD_REQUEST_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_RESPONSE,
    },
)
async def get_posts_feed(
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
        "Возвращает пост по его ID, включая количество лайков " "и комментариев."
    ),
    responses={
        200: {
            "description": "Пост найден",
            "content": {"application/json": {"example": SINGLE_POST_EXAMPLE}},
        },
        400: BAD_REQUEST_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        404: NOT_FOUND_RESPONSE,
        422: VALIDATION_RESPONSE,
    },
)
async def get_post(
    post_id: Annotated[
        int,
        Path(
            description="ID поста",
            openapi_examples=POST_ID_EXAMPLES,
        ),
    ],
    sub: GetSubDep,
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
    responses={
        200: {
            "description": "Пост обновлён",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            **POST_EXAMPLE,
                            "content": "Обновлённый текст поста.",
                        }
                    }
                }
            },
        },
        400: BAD_REQUEST_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        403: FORBIDDEN_RESPONSE,
        404: NOT_FOUND_RESPONSE,
        422: VALIDATION_RESPONSE,
    },
)
async def edit_post(
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
        "Удалить пост может только его автор."
    ),
    responses={
        200: {
            "description": "Пост удалён",
            "content": {"application/json": {"example": DELETE_EXAMPLE}},
        },
        400: BAD_REQUEST_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        403: FORBIDDEN_RESPONSE,
        404: NOT_FOUND_RESPONSE,
        422: VALIDATION_RESPONSE,
    },
)
async def delete_post(
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
