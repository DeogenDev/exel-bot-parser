"""Настройки приложения."""

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings


class BotConfig(BaseModel):
    """Настройки бота."""

    token: str
    parse_channel_id: str
    managers: list[int]

    @field_validator("managers")
    def validate_managers(cls, value):
        if isinstance(value, int):
            return [int(v.strip()) for v in value.split(",")]
        return value


class GooglConfig(BaseModel):
    """Настройки Google Auth."""

    credentials_path: str = "storage/credentials.json"
    sheet_name: str = ""
    spreadsheet_id: str = ""


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
