from typing import Any

from src.schemas.errors import ErrorResponseDTO

CREATE_COMMENT_RESPONSES: dict[int | str, dict[str, Any]] = {
    201: {
        "description": "Комментарий успешно создан",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "post_id": 10,
                    "user_id": 2,
                    "content": "Отличный пост! Спасибо за информацию.",
                    "created_at": "2026-10-13T12:00:00",
                    "updated_at": "2026-10-13T12:00:00",
                }
            }
        },
    },
    500: {
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
        "description": "Указанный пост не найден",
        "content": {
            "application/json": {
                "example": {
                    "error": "POST_NOT_FOUND",
                    "message": "Пост не найден",
                }
            }
        },
    },
    422: {
        "model": ErrorResponseDTO,
        "description": "Некорректный ID поста или текст комментария",
        "content": {
            "application/json": {
                "example": {
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                }
            }
        },
    },
}


GET_COMMENTS_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Список комментариев успешно получен",
        "content": {
            "application/json": {
                "example": {
                    "page": 1,
                    "per_page": 5,
                    "total_pages": 1,
                    "data": [
                        {
                            "id": 1,
                            "post_id": 10,
                            "user_id": 2,
                            "content": "Отличный пост!",
                            "created_at": "2026-10-13T12:00:00",
                            "updated_at": "2026-10-13T12:00:00",
                        },
                        {
                            "id": 2,
                            "post_id": 10,
                            "user_id": 3,
                            "content": "Спасибо за информацию!",
                            "created_at": "2026-10-13T12:10:00",
                            "updated_at": "2026-10-13T12:10:00",
                        },
                    ],
                }
            }
        },
    },
    500: {
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
    404: {
        "model": ErrorResponseDTO,
        "description": "Указанный пост не найден",
        "content": {
            "application/json": {
                "example": {
                    "error": "POST_NOT_FOUND",
                    "message": "Пост не найден",
                }
            }
        },
    },
    422: {
        "model": ErrorResponseDTO,
        "description": "Некорректные параметры пагинации или ID поста",
        "content": {
            "application/json": {
                "example": {
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                }
            }
        },
    },
}


GET_COMMENT_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Комментарий успешно получен",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "post_id": 10,
                    "user_id": 2,
                    "content": "Отличный пост!",
                    "created_at": "2026-10-13T12:00:00",
                    "updated_at": "2026-10-13T12:00:00",
                }
            }
        },
    },
    500: {
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
    404: {
        "model": ErrorResponseDTO,
        "description": "Комментарий не найден",
        "content": {
            "application/json": {
                "example": {
                    "error": "COMMENT_NOT_FOUND",
                    "message": "Комментарий не найден",
                }
            }
        },
    },
    422: {
        "model": ErrorResponseDTO,
        "description": "Некорректный ID поста или комментария",
        "content": {
            "application/json": {
                "example": {
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                }
            }
        },
    },
}


UPDATE_COMMENT_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Комментарий успешно обновлён",
        "content": {
            "application/json": {
                "example": {
                    "id": 1,
                    "post_id": 10,
                    "user_id": 2,
                    "content": "Обновлённый текст комментария.",
                    "created_at": "2026-10-13T12:00:00",
                    "updated_at": "2026-10-13T13:00:00",
                }
            }
        },
    },
    500: {
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
    403: {
        "model": ErrorResponseDTO,
        "description": "Недостаточно прав. Редактировать комментарий может только автор",
        "content": {
            "application/json": {
                "example": {
                    "error": "FORBIDDEN",
                    "message": "Доступ запрещен",
                }
            }
        },
    },
    404: {
        "model": ErrorResponseDTO,
        "description": "Комментарий не найден",
        "content": {
            "application/json": {
                "example": {
                    "error": "COMMENT_NOT_FOUND",
                    "message": "Комментарий не найден",
                }
            }
        },
    },
    422: {
        "model": ErrorResponseDTO,
        "description": "Некорректный ID или текст комментария",
        "content": {
            "application/json": {
                "example": {
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                }
            }
        },
    },
}


DELETE_COMMENT_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Комментарий успешно удалён",
        "content": {"application/json": {"example": {"data": {"deleted_count": 1}}}},
    },
    500: {
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
    403: {
        "model": ErrorResponseDTO,
        "description": "Недостаточно прав. Удалить комментарий может только автор",
        "content": {
            "application/json": {
                "example": {
                    "error": "FORBIDDEN",
                    "message": "Доступ запрещен",
                }
            }
        },
    },
    404: {
        "model": ErrorResponseDTO,
        "description": "Комментарий не найден",
        "content": {
            "application/json": {
                "example": {
                    "error": "COMMENT_NOT_FOUND",
                    "message": "Комментарий не найден",
                }
            }
        },
    },
    422: {
        "model": ErrorResponseDTO,
        "description": "Некорректный ID поста или комментария",
        "content": {
            "application/json": {
                "example": {
                    "error": "VALIDATION_ERROR",
                    "message": "Invalid request data",
                }
            }
        },
    },
}
