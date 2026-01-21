"""Мидлвар для контекста."""

from aiogram import BaseMiddleware

from src.utils import MessageExtractor
from src.service import IdsRedisStorage, MessageCleanupService


class ContextMiddleware(BaseMiddleware):
    """Middleware that injects parsing chat ID and extractor into handlers."""

    def __init__(
        self,
        parsing_chat_id: int,
        messages_extractor: MessageExtractor,
        redis_client: IdsRedisStorage,
        message_cleanup_service: MessageCleanupService,
    ):
        """Initialize middleware."""
        self.parsing_chat_id = parsing_chat_id
        self.messages_extractor = messages_extractor
        self.redis_client = redis_client
        self.message_cleanup_service = message_cleanup_service

    async def __call__(self, handler, event, data):
        """Inject parsing chat ID and extractor into handler."""
        data["parsing_chat_id"] = self.parsing_chat_id
        data["messages_extractor"] = self.messages_extractor
        data["redis_client"] = self.redis_client
        data["message_cleanup_service"] = self.message_cleanup_service
        return await handler(event, data)
