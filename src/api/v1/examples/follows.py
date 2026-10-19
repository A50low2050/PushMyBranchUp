from src.schemas.errors import ErrorResponseDTO

TOGGLE_FOLLOW_RESPONSES = {
    200: {
        "description": "Состояние подписки успешно изменено",
        "content": {
            "application/json": {
                "examples": {
                    "follow": {
                        "summary": "Подписка оформлена",
                        "value": {
                            "follower_id": 1,
                            "followed_id": 2,
                            "followed": True,
                        },
                    },
                    "unfollow": {
                        "summary": "Подписка отменена",
                        "value": {
                            "follower_id": 1,
                            "followed_id": 2,
                            "followed": False,
                        },
                    },
                }
            }
        },
    },
    400: {
        "model": ErrorResponseDTO,
        "description": "Нельзя подписаться на самого себя",
        "content": {
            "application/json": {
                "example": {
                    "error": "BAD_REQUEST",
                    "message": "Запрошенное действие невозможно выполнить",
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
        "description": "Пользователь с указанным ID не найден",
        "content": {
            "application/json": {
                "example": {
                    "error": "USER_NOT_FOUND",
                    "message": "Пользователь не найден",
                }
            }
        },
    },
    422: {
        "model": ErrorResponseDTO,
        "description": "Некорректный ID пользователя",
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
