from datetime import datetime

from src.schemas.base import BaseDTO


class UserDTO(BaseDTO):
    id: int
    username: str
    email: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
