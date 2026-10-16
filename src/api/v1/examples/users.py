from src.schemas.errors import ErrorResponseDTO


GET_USERS_RESPONSES = {
        200: {
            "description": "Список пользователей успешно получен",
            "content": {
                "application/json": {
                    "example": {
                        "page": 1,
                        "per_page": 5,
                        "total_pages": 1,
                        "data": [
                            {
                                "id": 1,
                                "username": "alex",
                                "email": "alex@example.com",
                                "created_at": "2026-10-13T12:00:00",
                                "updated_at": "2026-10-13T12:00:00",
                            },
                            {
                                "id": 2,
                                "username": "maria",
                                "email": "maria@example.com",
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
        401: {
            "model": ErrorResponseDTO,
            "description": "Пользователь не авторизован",
        },
        422: {
            "model": ErrorResponseDTO,
            "description": "Некорректные параметры пагинации",
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


GET_USER_RESPONSES = {
        200: {
            "description": "Пользователь успешно найден",
            "content": {
                "application/json": {
                    "example": {
                        "data": {
                            "id": 1,
                            "username": "alex",
                            "email": "alex@example.com",
                            "created_at": "2026-10-13T12:00:00",
                            "updated_at": "2026-10-13T12:00:00",
                        }
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
