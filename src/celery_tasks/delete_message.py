"""Задача на удаление сообщений."""

import asyncio
import logging

from aiogram import Bot

from src.shared import conf
from src.shared import send_telegram_message
from src.celery_app import app


logger = logging.getLogger(__name__)


@app.task(name="delete_messages_task", bind=True, queue="cleanup")
def delete_messages_task(self, message_ids: list[int], user_id: int) -> None:
    """
    Асинхронное удаление сообщений через TG-бота.
    """
    logger.info(f"Deleting {len(message_ids)} messages")

    bot = Bot(token=conf.bot.token)
    int_chat_id = int(conf.bot.parse_channel_id)

    async def _delete():
        logger.info(f"Deleting {len(message_ids)} messages")
        for message_id in message_ids:
            try:
                await bot.delete_message(
                    chat_id=int_chat_id,
                    message_id=message_id,
                )
                await asyncio.sleep(0.05)
                logger.info(f"Deleted message {message_id}")
            except Exception as e:
                logger.error(f"Failed to delete {message_id}: {e}")
        await send_telegram_message(
            chat_id=user_id,
            text=f"🚫 Удалено {len(message_ids)} сообщений.",
        )

    asyncio.run(_delete())
