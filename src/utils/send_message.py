"""Незавасимая отправка сообщения"""

import logging
from aiogram import Bot

from src.shared import conf

logger = logging.getLogger(__name__)


async def send_telegram_message(
    chat_id: int,
    text: str,
    thread_id: int = None,
) -> None:
    try:
        async with Bot(token=conf.bot.token).context() as bot:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                message_thread_id=thread_id,
            )
    except Exception as e:
        logging.error(f"Failed to send message: {e}")
        raise
