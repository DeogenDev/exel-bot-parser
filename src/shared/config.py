"""Настройки приложения."""

from pydantic import BaseModel
from pydantic_settings import BaseSettings


class BotConfig(BaseModel):
    """Настройки бота."""

    token: str
    parse_channel_id: str


class GooglConfig(BaseModel):
    """Настройки Google Auth."""

    credentials_path: str = "storage/credentials.json"
    token_path: str = "storage/token.json"


class RedisConfig(BaseModel):
    """Данные конфигурации Redis."""

    host: str
    port: int


class Config(BaseSettings):
    """Настройки приложения."""

    bot: BotConfig
    google: GooglConfig
    redis: RedisConfig

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


conf = Config()
