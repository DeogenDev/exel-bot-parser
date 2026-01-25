"""Сервис для передачи сообщений на перенос."""

import logging
from typing import Callable
from src.service import MessageRedisStorage

logger = logging.getLogger(__name__)


class MessageTransferService:
    def __init__(self, storage: MessageRedisStorage, transfer_messages_task: Callable):
        self._storage = storage
        self.transfer_messages_task = transfer_messages_task

    async def transfer_messages(self, user_id: int) -> None:
        ids = await self._storage.get_all_messages()
        texts = list(ids.values())
        logger.info(f"Put to transferd {len(ids)} messages")
        if ids:
            self.transfer_messages_task.delay(texts, user_id)
