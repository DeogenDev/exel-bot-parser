"""Мидлвар для контекста."""

from aiogram import BaseMiddleware

from src.service import (
    MessageRedisStorage,
    MessageCleanupService,
    MessageTransferService,
)


class ContextMiddleware(BaseMiddleware):
    """Middleware that injects parsing chat ID and extractor into handlers."""

    def __init__(
        self,
        parsing_chat_id: int,
        redis_client: MessageRedisStorage,
        message_cleanup_service: MessageCleanupService,
        message_transfer_service: MessageTransferService,
    ):
        """Initialize middleware."""
        self.parsing_chat_id = parsing_chat_id
        self.redis_client = redis_client
        self.message_cleanup_service = message_cleanup_service
        self.message_transfer_service = message_transfer_service

    async def __call__(self, handler, event, data):
        """Inject parsing chat ID and extractor into handler."""
        data["parsing_chat_id"] = self.parsing_chat_id
        data["redis_client"] = self.redis_client
        data["message_cleanup_service"] = self.message_cleanup_service
        data["message_transfer_service"] = self.message_transfer_service
        return await handler(event, data)
