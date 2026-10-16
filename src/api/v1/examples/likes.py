from src.schemas.errors import ErrorResponseDTO


TOGGLE_LIKE_RESPONSES = {
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
            "description": "Пост с указанным ID не найден",
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
    }
