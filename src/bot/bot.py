"""Инициализация бота."""

import logging
from aiogram import Bot, Dispatcher

from .handlers import group_message_router

logger = logging.getLogger(__name__)


class MessageParserBot:
    def __init__(self, token: str, parse_channel_id: str):
        self.bot = Bot(token)
        self.parsing_chat_id = parse_channel_id
        self.dp = Dispatcher()

    async def run(self):
        """Запуск бота."""
        self.dp.include_routers(group_message_router)
        await self.dp.start_polling(self.bot)
