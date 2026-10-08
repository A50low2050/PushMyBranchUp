class ApplicationBaseError(Exception):
    detail: str = "Произошла ошибка в приложении"

    def __init__(self, detail: str | None = None):
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class ObjectNotFoundError(ApplicationBaseError):
    detail = "Объект не найден"


class UserNotFoundError(ObjectNotFoundError):
    detail = "Пользователь не найден"


class ObjectAlreadyExistsError(ApplicationBaseError):
    detail = "Объект уже существует"


class DBConnectionError(ApplicationBaseError):
    detail = "Ошибка соединения с базой данных"


class CacheConnectionError(ApplicationBaseError):
    detail = "Ошибка соединения с кэшем"


class DBIntValueOutOfRangeError(ApplicationBaseError):
    detail = "Числовое значение вне допустимого диапазона"


class DBQueryError(ApplicationBaseError):
    detail = "Ошибка запроса к базе данных"


class InvalidLoginDataError(ApplicationBaseError):
    detail = "Неверные логин или пароль для входа"
