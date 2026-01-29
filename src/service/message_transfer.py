"""Сервис для передачи сообщений на перенос."""

import logging
import asyncio
from aiogram import Bot
from typing import Callable

from aiogram.types import ReactionTypeEmoji

from src.shared import conf
from src.service import MessageRedisStorage

logger = logging.getLogger(__name__)


class MessageTransferService:
    def __init__(self, storage: MessageRedisStorage, transfer_messages_task: Callable):
        self._storage = storage
        self.transfer_messages_task = transfer_messages_task
        self._semaphore = asyncio.Semaphore(5)
        self.bot: Bot

    async def transfer_messages(self, user_id: int, bot: Bot) -> None:
        messages_map = await self._storage.get_all_messages()
        if not messages_map:
            logger.info("No messages in storage to transfer.")
            return

        checked_ids = await asyncio.gather(
            *(self._get_id_if_exists(m_id, bot) for m_id in messages_map.keys())
        )

        exists_texts = [
            messages_map[m_id]
            for m_id in checked_ids
            if m_id is not None and m_id in messages_map
        ]

        logger.info(f"User {user_id}: {len(exists_texts)} messages verified.")

        if exists_texts:
            self.transfer_messages_task.delay(exists_texts, user_id)

    async def _get_id_if_exists(self, message_id: int, bot: Bot) -> int | None:
        async with self._semaphore:
            try:
                await bot.set_message_reaction(
                    chat_id=conf.bot.parse_channel_id,
                    message_id=message_id,
                    reaction=[ReactionTypeEmoji(emoji="🔥")],
                )
                return message_id
            except Exception:
                return None
