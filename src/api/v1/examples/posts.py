from src.api.v1.examples.common import error_response


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
        "comments": 2,
        "likes": 5,
        "posts": 1,
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


DB_ERROR_RESPONSE = error_response(
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


CREATE_POST_RESPONSES = {
        201: {
            "description": "Пост создан",
            "content": {"application/json": {"example": SINGLE_POST_EXAMPLE}},
        },
        500: DB_ERROR_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_RESPONSE,
    }



GET_POSTS_RESPONSES = {
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
        500: DB_ERROR_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_RESPONSE,
    }


GET_POSTS_FEED_RESPONSES = {
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
        500: DB_ERROR_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        422: VALIDATION_RESPONSE,
    }


GET_POST_RESPONSES = {
        200: {
            "description": "Пост найден",
            "content": {"application/json": {"example": SINGLE_POST_EXAMPLE}},
        },
        500: DB_ERROR_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        404: NOT_FOUND_RESPONSE,
        422: VALIDATION_RESPONSE,
    }


EDIT_POST_RESPONSES = {
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
        500: DB_ERROR_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        403: FORBIDDEN_RESPONSE,
        404: NOT_FOUND_RESPONSE,
        422: VALIDATION_RESPONSE,
    }


DELETE_POST_RESPONSES = {
        200: {
            "description": "Пост удалён",
            "content": {"application/json": {"example": DELETE_EXAMPLE}},
        },
        500: DB_ERROR_RESPONSE,
        401: UNAUTHORIZED_RESPONSE,
        403: FORBIDDEN_RESPONSE,
        404: NOT_FOUND_RESPONSE,
        422: VALIDATION_RESPONSE,
    }
