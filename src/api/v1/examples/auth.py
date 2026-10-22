from typing import Any

from src.schemas.errors import ErrorResponseDTO

GET_ME_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Данные пользователя получены",
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
    401: {
        "model": ErrorResponseDTO,
        "description": "Пользователь не авторизован",
        "content": {
            "application/json": {
                "example": {
                    "error": "UNAUTHORIZED",
                    "message": "Пользователь не авторизован",
                }
            }
        },
    },
}


REGISTER_RESPONSES: dict[int | str, dict[str, Any]] = {
    201: {
        "description": "Пользователь успешно зарегистрирован",
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
    409: {
        "model": ErrorResponseDTO,
        "description": "Пользователь с такими данными уже существует",
        "content": {
            "application/json": {
                "example": {
                    "error": "USER_ALREADY_EXISTS",
                    "message": "Пользователь уже существует",
                }
            }
        },
    },
    422: {
        "model": ErrorResponseDTO,
        "description": "Ошибка валидации данных регистрации",
        "content": {
            "application/json": {
                "examples": {
                    "empty_password": {
                        "summary": "Пустой пароль",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Пароль не может быть пустым",
                        },
                    },
                    "short_password": {
                        "summary": "Короткий пароль",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Пароль должен содержать минимум 8 символов",
                        },
                    },
                    "long_password": {
                        "summary": "Длинный пароль",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Пароль не может превышать 128 символов",
                        },
                    },
                    "empty_username": {
                        "summary": "Пустой логин",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Логин не может быть пустым",
                        },
                    },
                    "short_username": {
                        "summary": "Короткий логин",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Логин должен содержать минимум 3 символа",
                        },
                    },
                    "long_username": {
                        "summary": "Длинный логин",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Логин не может превышать 255 символов",
                        },
                    },
                    "empty_email": {
                        "summary": "Пустая почта",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Электронная почта не может быть пустой",
                        },
                    },
                    "invalid_email": {
                        "summary": "Неверный формат почты",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Некорректный адрес электронной почты",
                        },
                    },
                }
            }
        },
    },
}


LOGIN_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Вход выполнен успешно",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "example.access.token",
                    "refresh_token": "example.refresh.token",
                    "type": "Bearer",
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
        "description": "Неверная электронная почта или пароль",
        "content": {
            "application/json": {
                "example": {
                    "error": "INVALID_LOGIN_DATA",
                    "message": "Неверные логин или пароль",
                }
            }
        },
    },
    422: {
        "model": ErrorResponseDTO,
        "description": "Некорректные данные для входа",
        "content": {
            "application/json": {
                "examples": {
                    "empty_password": {
                        "summary": "Пустой пароль",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Пароль не может быть пустым",
                        },
                    },
                    "empty_email": {
                        "summary": "Пустая почта",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Электронная почта не может быть пустой",
                        },
                    },
                    "invalid_email": {
                        "summary": "Неверный формат почты",
                        "value": {
                            "error": "VALIDATION_ERROR",
                            "message": "Некорректный адрес электронной почты",
                        },
                    },
                }
            }
        },
    },
}


REFRESH_TOKEN_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Токены успешно обновлены",
        "content": {
            "application/json": {
                "example": {
                    "access_token": "new.example.access.token",
                    "refresh_token": "new.example.refresh.token",
                    "type": "Bearer",
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
        "description": "Refresh-токен отсутствует, недействителен или истёк",
    },
    404: {
        "model": ErrorResponseDTO,
        "description": "Пользователь не найден",
        "content": {
            "application/json": {
                "example": {
                    "error": "USER_NOT_FOUND",
                    "message": "Пользователь не найден",
                }
            }
        },
    },
}


LOGOUT_RESPONSES: dict[int | str, dict[str, Any]] = {
    204: {
        "description": "Выход выполнен успешно. Тело ответа отсутствует.",
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
        "description": "Пользователь не авторизован или токен недействителен",
    },
}


UPDATE_ME_RESPONSES: dict[int | str, dict[str, Any]] = {
    200: {
        "description": "Имя пользователя успешно изменено",
        "content": {
            "application/json": {
                "example": {
                    "data": {
                        "id": 1,
                        "username": "alex_new",
                        "email": "alex@example.com",
                        "created_at": "2026-10-13T12:00:00",
                        "updated_at": "2026-10-13T13:00:00",
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
        "description": "Пользователь не найден",
        "content": {
            "application/json": {
                "example": {
                    "error": "USER_NOT_FOUND",
                    "message": "Пользователь не найден",
                }
            }
        },
    },
    409: {
        "model": ErrorResponseDTO,
        "description": "Имя пользователя уже занято",
        "content": {
            "application/json": {
                "example": {
                    "error": "USER_ALREADY_EXISTS",
                    "message": "Пользователь уже существует",
                }
            }
        },
    },
    422: {
        "model": ErrorResponseDTO,
        "description": "Некорректное имя пользователя",
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
