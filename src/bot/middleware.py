"""Мидлвар для контекста."""

from typing import Union

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from src.service import (
    MessageRedisStorage,
    MessageCleanupService,
    MessageTransferService,
)

from src.shared import conf


class ContextMiddleware(BaseMiddleware):
    """Middleware that injects parsing chat ID and extractor into handlers."""

    def __init__(
        self,
        parsing_chat_id: int,
        redis_client: MessageRedisStorage,
        message_cleanup_service: MessageCleanupService,
        message_transfer_service: MessageTransferService,
        parse_topic_id: int,
        logs_topic_id: int,
    ):
        """Initialize middleware."""
        self.parsing_chat_id = parsing_chat_id
        self.redis_client = redis_client
        self.message_cleanup_service = message_cleanup_service
        self.message_transfer_service = message_transfer_service
        self.parse_topic_id = parse_topic_id
        self.logs_topic_id = logs_topic_id

    async def __call__(self, handler, event, data):
        """Inject parsing chat ID and extractor into handler."""
        data["parsing_chat_id"] = self.parsing_chat_id
        data["redis_client"] = self.redis_client
        data["message_cleanup_service"] = self.message_cleanup_service
        data["message_transfer_service"] = self.message_transfer_service
        data["parse_topic_id"] = self.parse_topic_id
        data["logs_topic_id"] = self.logs_topic_id
        return await handler(event, data)


class AuthMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        self.managers = set(conf.bot.managers)

    async def __call__(
        self,
        handler,
        event: Union[Message, CallbackQuery],
        data: dict,
    ) -> None:
        user_id = event.from_user.id

        if user_id in self.managers:
            return await handler(event, data)

        return None
