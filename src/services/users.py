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


class UsersService(BaseService):
    async def login(
        self,
        data: UserLoginDTO,
        cache: AsyncCacheServiceBase,
    ) -> IssuedTokens:
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

        rf_token: RefreshTokenDTO | None = await self.db.rf_tokens.get_one_or_none(
            owner_id=user.id,
        )  # type: ignore
        if rf_token:
            await TokenService(self.db).blacklist_ac_token(
                rf_token=rf_token,
                cache=cache,
            )
        tokens = await TokenService(self.db).update_tokens(user=user, cache=cache)
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
                id=token.owner_id
            )  # type: ignore
        except ObjectNotFoundError as exc:
            raise UserNotFoundError from exc

        await TokenService(self.db).blacklist_ac_token(rf_token=token, cache=cache)
        tokens = await TokenService(self.db).update_tokens(
            user=user,
            cache=cache,
        )
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
            raise UserNotFoundError from exc

        user_schema = UserResponseDTO.model_validate(result)
        return user_schema

    async def logout(
        self,
        rf_token: RefreshTokenDTO,
        user_id: int,
        cache: AsyncCacheServiceBase,
    ) -> None:
        """Логика выхода из пользовательского аккаунта"""

        jti = rf_token.access_jti
        exp_timestamp = rf_token.expires_at + settings.auth.access_token_expire_delta

        key = f"{settings.auth.access_token_blacklist_prefix}{jti}"
        remaining_ttl = (
            exp_timestamp.astimezone(UTC) - datetime.now(UTC)
        ).total_seconds()
        if remaining_ttl > 0:
            await cache.setx(key, 1, int(remaining_ttl))

        await self.db.rf_tokens.delete(
            owner_id=user_id,
            hashed_data=rf_token.hashed_data,
        )
        await self.db.commit()

    async def update_user(self, user_id: int, data: UserUpdateDTO) -> UserResponseDTO:
        """Обновление данных о пользователе"""

        try:
            user: UserDTO = await self.db.users.get_one(id=user_id)  # type: ignore
        except ObjectNotFoundError as exc:
            raise UserNotFoundError from exc

        user_schema = UserResponseDTO.model_validate(user)
        if user.username == data.username:
            return user_schema

        try:
            result = await self.db.users.update(data, id=user_id)
        except ObjectAlreadyExistsError as exc:
            raise UserAlreadyExistsError from exc

        if not result:
            raise UserNotFoundError

        await self.db.commit()
        user_schema.username = data.username
        return user_schema
