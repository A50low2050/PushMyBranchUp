from src.models.users import UserORM
from src.repos.base import BaseRepo
from src.schemas.users import UserDTO


class UsersRepo(BaseRepo):
    model = UserORM
    schema = UserDTO
