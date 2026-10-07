from src.models.base import CommonBaseORM
from src.repos.base import BaseRepo
from src.schemas.tokens import RefreshTokenDTO


class RefreshTokensRepo(BaseRepo):
    # TODO: добавить модели для токенов
    model = CommonBaseORM
    schema = RefreshTokenDTO
