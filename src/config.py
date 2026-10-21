from datetime import timedelta
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parent.parent


class UvicornSettings(BaseModel):
    """настройки для uvicorn"""

    host: str
    port: int
    reload: bool


class FastAPISettings(BaseModel):
    """настройки приложения"""

    name: str = "Соцсеть «Push My Branch Up!»"
    description: str = "Социальная сеть для обмена идеями внутри группы"
    root_path: str = "/api"


class DBSettings(BaseModel):
    """настройки базы данных"""

    url: str
    echo: bool = False
    autocommit: bool = False
    autoflush: bool = False
    expire_on_commit: bool = False


class CookieSettings(BaseModel):
    """настройки cookie для refresh-токена"""

    key: str = "refresh_token"
    max_age: int = 30 * 24 * 60 * 60
    httponly: bool = True
    samesite: Literal["lax", "strict", "none"] = "lax"
    secure: bool = False
    path: str = "/"
    domain: str | None = None

    @field_validator("max_age", mode="before")
    @classmethod
    def parse_max_age(cls, v: Any) -> int:
        if isinstance(v, timedelta):
            return int(v.total_seconds())
        return int(v)

    @property
    def name(self) -> str:
        return self.key


class AuthSettings(BaseModel):
    """настройки аутентификации"""

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_delta: timedelta = timedelta(minutes=15)
    refresh_token_expire_delta: timedelta = timedelta(days=30)
    access_token_blacklist_prefix: str = "blacklist:"

    @property
    def refresh_token_cookie_name(self) -> str:
        return settings.cookie.key

    @property
    def cookie(self) -> CookieSettings:
        return settings.cookie

    @property
    def cookies(self) -> CookieSettings:
        return settings.cookie


class SMTPEmailNotificationsSettings(BaseModel):
    host: str = "localhost"
    port: int = 587
    user: str = ""
    password: SecretStr = SecretStr("")
    from_email: str = ""
    use_tls: bool = True
    start_tls: bool = False
    timeout_seconds: float = 15.0


class NotificationsSettings(BaseModel):
    enabled: bool = True
    auto_disable_on_error: bool = True
    email: SMTPEmailNotificationsSettings = SMTPEmailNotificationsSettings()


class RateLimitSettings(BaseModel):
    """настройки ограничения частоты запросов (Rate Limiting)"""

    enabled: bool = True
    default_limit: str = "100/minute"
    auth_limit: str = "30/minute"
    posts_limit: str = "60/minute"
    comments_limit: str = "60/minute"
    likes_limit: str = "100/minute"
    follows_limit: str = "60/minute"
    users_limit: str = "100/minute"


class Settings(BaseSettings):
    """настройки приложения"""

    uvicorn: UvicornSettings
    database: DBSettings
    auth: AuthSettings
    notifications: NotificationsSettings
    rate_limit: RateLimitSettings = RateLimitSettings()
    fastapi: FastAPISettings = FastAPISettings()
    cookie: CookieSettings = CookieSettings()

    @property
    def cookies(self) -> CookieSettings:
        return self.cookie

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="ENV_",
    )


settings = Settings()  # type: ignore
