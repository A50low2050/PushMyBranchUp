from fastapi import HTTPException, status


class ApplicationHTTPError(HTTPException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Ошибка на стороне сервера"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(status_code=self.status_code, detail=self.detail)


class NotFoundHTTPError(ApplicationHTTPError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Объект не найден"


class ObjectAlreadyExistsHTTPError(ApplicationHTTPError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Объект уже существует"


class UnauthorizedHTTPError(ApplicationHTTPError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Пользователь не авторизован"


class ForbiddenHTTPError(ApplicationHTTPError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Доступ запрещен"


class BadRequestHTTPError(ApplicationHTTPError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Запрошенное действие невозможно выполнить"
