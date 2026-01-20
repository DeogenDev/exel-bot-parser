"""Инициализация бота."""

import logging
from aiogram import Bot, Dispatcher

from .handlers import group_message_router
from .middleware import ContextMiddleware
from src.utils import MessageExtractor

logger = logging.getLogger(__name__)


class MessageParserBot:
    def __init__(
        self, token: str, parse_channel_id: str, messages_extractor: MessageExtractor
    ):
        self.bot = Bot(token)
        self.parsing_chat_id = parse_channel_id
        self.dp = Dispatcher()
        self.messages_extractor = messages_extractor

    async def run(self):
        """Запуск бота."""
        self.dp.update.middleware(
            ContextMiddleware(self.parsing_chat_id, self.messages_extractor)
        )
        self.dp.include_routers(group_message_router)
        await self.dp.start_polling(self.bot)
