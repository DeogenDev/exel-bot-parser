"""Мидлвар для контекста."""

from aiogram import BaseMiddleware
from src.utils import MessageExtractor


class ContextMiddleware(BaseMiddleware):
    """Middleware that injects parsing chat ID and extractor into handlers."""

    def __init__(self, parsing_chat_id: int, messages_extractor: MessageExtractor):
        """Initialize middleware."""
        self.parsing_chat_id = parsing_chat_id
        self.messages_extractor = messages_extractor

    async def __call__(self, handler, event, data):
        """Inject parsing chat ID and extractor into handler."""
        data["parsing_chat_id"] = self.parsing_chat_id
        data["messages_extractor"] = self.messages_extractor
        return await handler(event, data)
