"""Инициализация бота."""

import logging
from aiogram import Bot, Dispatcher

from .handlers import (
    transfer_orders_router,
    menu_router,
    start_router,
    clear_chat_router,
    on_group_message_router,
)
from .middleware import ContextMiddleware
from src.service import (
    MessageRedisStorage,
    MessageCleanupService,
    MessageTransferService,
)

logger = logging.getLogger(__name__)


class MessageParserBot:
    def __init__(
        self,
        token: str,
        parse_channel_id: str,
        redis_client: MessageRedisStorage,
        message_cleanup_service: MessageCleanupService,
        message_transfer_service: MessageTransferService,
    ):
        self.bot = Bot(token)
        self.parsing_chat_id = parse_channel_id
        self.dp = Dispatcher()
        self.redis_client = redis_client
        self.message_cleanup_service = message_cleanup_service
        self.message_transfer_service = message_transfer_service

    async def run(self):
        """Запуск бота."""
        self.dp.update.middleware(
            ContextMiddleware(
                self.parsing_chat_id,
                self.redis_client,
                self.message_cleanup_service,
                self.message_transfer_service,
            )
        )
        self.dp.include_routers(
            transfer_orders_router,
            menu_router,
            start_router,
            clear_chat_router,
            on_group_message_router,
        )
        await self.dp.start_polling(self.bot)
