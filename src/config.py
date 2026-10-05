from pathlib import Path

from pydantic import BaseModel
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


class Settings(BaseSettings):
    """настройки приложения"""

    uvicorn: UvicornSettings
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
