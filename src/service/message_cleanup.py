"""Сервис очистки сообщений."""

import logging
from typing import Callable
from src.service import MessageRedisStorage

logger = logging.getLogger(__name__)


class MessageCleanupService:
    def __init__(self, storage: MessageRedisStorage, delete_messages_task: Callable):
        self._storage = storage
        self.delete_messages_task = delete_messages_task

    async def remove_all_messages(self) -> None:
        ids = await self._storage.remove_all_messages()
        logger.info(f"Put to deleted {len(ids)} messages")
        if ids:
            self.delete_messages_task.delay(ids)
