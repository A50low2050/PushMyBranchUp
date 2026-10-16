from copy import deepcopy
from typing import Any


ERROR_EXAMPLES: dict[str, dict[str, str]] = {
    "400": {
        "error": "HTTP_ERROR",
        "message": "Некорректный запрос",
    },
    "401": {
        "error": "UNAUTHORIZED",
        "message": "Требуется авторизация",
    },
    "403": {
        "error": "HTTP_ERROR",
        "message": "Недостаточно прав для выполнения операции",
    },
    "404": {
        "error": "HTTP_ERROR",
        "message": "Запрашиваемый ресурс не найден",
    },
    "405": {
        "error": "HTTP_ERROR",
        "message": "Метод не поддерживается",
    },
    "409": {
        "error": "HTTP_ERROR",
        "message": "Конфликт данных",
    },
    "422": {
        "error": "VALIDATION_ERROR",
        "message": "Invalid request data",
    },
    "429": {
        "error": "HTTP_ERROR",
        "message": "Слишком много запросов",
    },
    "500": {
        "error": "INTERNAL_SERVER_ERROR",
        "message": "Ошибка на стороне сервера",
    },
    "502": {
        "error": "HTTP_ERROR",
        "message": "Ошибка внешнего сервиса",
    },
    "503": {
        "error": "HTTP_ERROR",
        "message": "Сервис временно недоступен",
    },
}


def add_error_examples(openapi_schema: dict[str, Any]) -> None:
    """
    Добавляет конкретные примеры к уже описанным
    HTTP-ответам с ошибками.

    Не добавляет новые HTTP-коды.
    Не изменяет существующие примеры.
    Не изменяет обработку ошибок API.
    """

    paths = openapi_schema.get("paths", {})

    for path_item in paths.values():
        if not isinstance(path_item, dict):
            continue

        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue

            responses = operation.get("responses")

            if not isinstance(responses, dict):
                continue

            for status_code, response in responses.items():
                status_code = str(status_code)

                if not status_code.startswith(("4", "5")):
                    continue

                if not isinstance(response, dict):
                    continue

                # Не изменяем ответы, описанные через $ref.
                if "$ref" in response:
                    continue

                example = ERROR_EXAMPLES.get(status_code)

                if example is None:
                    continue

                content = response.get("content")

                if not isinstance(content, dict):
                    continue

                json_content = content.get("application/json")

                if not isinstance(json_content, dict):
                    continue

                # Сохраняем существующие примеры.
                if "example" in json_content:
                    continue

                if "examples" in json_content:
                    continue

                # Добавляем пример только в документацию.
                json_content["example"] = deepcopy(example)
