"""Инициализация бота."""

import logging
from aiogram import Bot, Dispatcher

from .handlers import (
    tranfer_orders_router,
    menu_router,
    start_router,
    clear_chat_router,
    on_group_message_router,
)
from .middleware import ContextMiddleware
from src.utils import MessageExtractor
from src.service import IdsRedisStorage, MessageCleanupService

logger = logging.getLogger(__name__)


class MessageParserBot:
    def __init__(
        self,
        token: str,
        parse_channel_id: str,
        messages_extractor: MessageExtractor,
        redis_client: IdsRedisStorage,
        message_cleanup_service: MessageCleanupService,
    ):
        self.bot = Bot(token)
        self.parsing_chat_id = parse_channel_id
        self.dp = Dispatcher()
        self.messages_extractor = messages_extractor
        self.redis_client = redis_client
        self.message_cleanup_service = message_cleanup_service

    async def run(self):
        """Запуск бота."""
        self.dp.update.middleware(
            ContextMiddleware(
                self.parsing_chat_id,
                self.messages_extractor,
                self.redis_client,
                self.message_cleanup_service,
            )
        )
        self.dp.include_routers(
            tranfer_orders_router,
            menu_router,
            start_router,
            clear_chat_router,
            on_group_message_router,
        )
        await self.dp.start_polling(self.bot)
