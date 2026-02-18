import logging
import asyncio
from aiogram import Bot
from typing import Callable
from aiogram.types import ReactionTypeEmoji
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest

from src.shared import conf
from src.service import MessageRedisStorage

logger = logging.getLogger(__name__)


class MessageTransferService:
    def __init__(
        self,
        storage: MessageRedisStorage,
        transfer_messages_task: Callable,
    ):
        self._storage = storage
        self.transfer_messages_task = transfer_messages_task

    async def transfer_messages(self, user_id: int, bot: Bot) -> None:
        messages_map = await self._storage.get_all_messages()
        if not messages_map:
            return

        exists_texts = []

        for message_id, text in messages_map.items():
            while True:
                try:
                    await bot.set_message_reaction(
                        chat_id=conf.bot.parse_channel_id,
                        message_id=int(message_id),
                        reaction=[ReactionTypeEmoji(emoji="🔥")],
                    )

                    exists_texts.append(text)

                    await asyncio.sleep(0.5)

                    break

                except TelegramRetryAfter as e:
                    logger.warning(
                        f"Flood limit. Sleeping {e.retry_after}s"
                    )
                    await asyncio.sleep(e.retry_after)

                except TelegramBadRequest:
                    logger.info(f"Message {message_id} not found.")
                    break

                except Exception as e:
                    logger.error(f"Unexpected error for {message_id}: {e}")
                    break

        logger.info(
            f"User {user_id}: {len(exists_texts)}/{len(messages_map)} verified."
        )

        if exists_texts:
            self.transfer_messages_task.delay(exists_texts, user_id)
