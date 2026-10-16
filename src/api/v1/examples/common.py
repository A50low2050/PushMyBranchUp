from src.schemas.errors import ErrorResponseDTO


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
