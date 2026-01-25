"""Модель сообщения."""

from pydantic import BaseModel


class TgMessage(BaseModel):
    """Модель сообщения."""

    id: int
    text: str
