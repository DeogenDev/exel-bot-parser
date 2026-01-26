"""Настройки приложения и бота."""

from .config import conf
from .send_message import send_telegram_message

__all__ = ("conf", "send_telegram_message")
