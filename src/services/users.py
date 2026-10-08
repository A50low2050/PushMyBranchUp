from datetime import UTC, datetime

from src.config import settings
from src.schemas.tokens import IssuedTokens, RefreshTokenDTO
from src.schemas.users import UserDTO, UserRegisterDTO
from src.services.auth import TokenService
from src.services.base import BaseService
from src.utils.cacheserv import AsyncCacheServiceBase
from src.utils.exceptions import (
    InvalidLoginDataError,
    ObjectNotFoundError,
    UserNotFoundError,
)
from src.utils.hashserv import PasswordService
from src.utils.logserv import LogService

logger = LogService.get_logger(__name__)


class UsersSerivce(BaseService):
    async def login(self, data: UserRegisterDTO) -> IssuedTokens:
        """Вход в аккаунт пользователя"""

        try:
            user: UserDTO = await self.db.users.get_one(
                email=data.email
            )  # type: ignore
        except ObjectNotFoundError as exc:
            raise InvalidLoginDataError from exc

        is_same = PasswordService.verify(data.password, user.hashed_password)
        if not is_same:
            raise InvalidLoginDataError

        tokens = await TokenService(self.db).update_tokens(user=user)
        await self.db.commit()
        return tokens

    async def refresh(
        self,
        token: RefreshTokenDTO,
        cache: AsyncCacheServiceBase,
    ) -> IssuedTokens:
        """Обновление Access и Refresh токенов"""

        try:
            user: UserDTO = await self.db.users.get_one(
                user_id=token.owner_id
            )  # type: ignore
        except ObjectNotFoundError as exc:
            raise UserNotFoundError from exc

        jti = token.access_jti
        key = f"{settings.auth.access_token_blacklist_prefix}{jti}"

        access_lifetime = settings.auth.access_token_expire_delta.total_seconds()
        access_exp = token.created_at.timestamp() + access_lifetime
        remaining_ttl = int(float(access_exp) - datetime.now(UTC).timestamp())

        if remaining_ttl > 0:
            await cache.setx(key, 1, remaining_ttl)

        tokens = await TokenService(self.db).update_tokens(user=user)
        await self.db.commit()
        return tokens

    async def register(self):
        raise NotImplementedError

    async def get_user(self):
        raise NotImplementedError

    async def logout(self):
        raise NotImplementedError

    async def update_user(self):
        raise NotImplementedError
