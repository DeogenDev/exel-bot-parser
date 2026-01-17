"""Инициализация бота."""

import logging
from aiogram import Bot, Dispatcher

logger = logging.getLogger(__name__)


class MessageParserBot:
    def __init__(self, token: str, parse_channel_id: str):
        self.bot = Bot(token)
        self.parsing_chat_id = parse_channel_id
        self.dp = Dispatcher()

    async def on_new_message(self, message):
        pass

    async def run(self):
        """Запуск бота."""
        self.dp.startup.register(self.on_new_message)
        await self.dp.start_polling(self.bot)
