from datetime import UTC, datetime

from src.config import settings
from src.schemas.tokens import IssuedTokens, RefreshTokenDTO
from src.schemas.users import (
    UserAddDTO,
    UserDTO,
    UserLoginDTO,
    UserRegisterDTO,
    UserResponseDTO,
    UserUpdateDTO,
)
from src.services.auth import TokenService
from src.services.base import BaseService
from src.utils.cacheserv import AsyncCacheServiceBase
from src.utils.exceptions import (
    InvalidLoginDataError,
    ObjectAlreadyExistsError,
    ObjectNotFoundError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.utils.hashserv import PasswordService
from src.utils.logserv import LogService

logger = LogService.get_logger(__name__)


class UsersSerivce(BaseService):
    async def login(self, data: UserLoginDTO) -> IssuedTokens:
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

    async def register(self, data: UserRegisterDTO) -> UserResponseDTO:
        hashed_pwd = PasswordService.hash_pwd(data.password)
        user = UserAddDTO(
            username=data.username,
            email=data.email,
            hashed_password=hashed_pwd,
        )

        try:
            result = await self.db.users.add(user)
            await self.db.commit()
        except ObjectAlreadyExistsError as exc:
            raise UserAlreadyExistsError from exc

        user_schema = UserResponseDTO.model_validate(result)
        return user_schema

    async def get_user(self, user_id: int) -> UserResponseDTO:
        try:
            result = await self.db.users.get_one(id=user_id)
        except ObjectNotFoundError as exc:
            raise InvalidLoginDataError from exc

        user_schema = UserResponseDTO.model_validate(result)
        return user_schema

    async def logout(
        self,
        access_t: dict,
        cache: AsyncCacheServiceBase,
    ) -> None:
        user_id = int(access_t["sub"])
        logger.info(f"Выход пользователя из системы user_id={user_id}")
        jti = access_t.get("jti")
        exp_timestamp = access_t.get("exp")

        if jti and exp_timestamp:
            key = f"{settings.auth.access_token_blacklist_prefix}{jti}"
            remaining_ttl = int(float(exp_timestamp) - datetime.now(UTC).timestamp())
            if remaining_ttl > 0:
                await cache.setx(key, 1, remaining_ttl)

        await self.db.rf_tokens.delete(owner_id=user_id)
        await self.db.commit()
        logger.info(f"Пользователь user_id={user_id} успешно вышел из системы")

    async def update_user(self, user_id: int, data: UserUpdateDTO) -> int:
        try:
            await self.db.users.get_one(id=user_id)
        except ObjectNotFoundError as exc:
            raise UserNotFoundError from exc

        try:
            result = await self.db.users.update(data, id=user_id)
        except ObjectAlreadyExistsError as exc:
            raise UserAlreadyExistsError from exc

        await self.db.commit()
        return result
