from datetime import timedelta
from pathlib import Path

from pydantic import BaseModel, SecretStr
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


class AuthSettings(BaseModel):
    """настройки аутентификации"""

    secret_key: SecretStr
    algorithm: str = "HS256"
    access_token_expire_delta: timedelta = timedelta(minutes=15)
    refresh_token_expire_delta: timedelta = timedelta(days=30)
    refresh_token_cookie_name: str = "refresh_token"
    access_token_blacklist_prefix: str = "blacklist:"


class Settings(BaseSettings):
    """настройки приложения"""

    uvicorn: UvicornSettings
    database: DBSettings
    auth: AuthSettings
    fastapi: FastAPISettings = FastAPISettings()

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="ENV_",
    )


settings = Settings()  # type: ignore
