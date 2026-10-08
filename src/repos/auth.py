from src.models.tokens import RefreshTokenORM
from src.repos.base import BaseRepo
from src.schemas.tokens import RefreshTokenDTO


class RefreshTokensRepo(BaseRepo):
    model = RefreshTokenORM
    schema = RefreshTokenDTO
