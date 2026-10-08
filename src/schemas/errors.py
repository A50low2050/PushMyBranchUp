from src.schemas.base import BaseDTO


class ErrorResponseDTO(BaseDTO):
    error: str
    message: str
