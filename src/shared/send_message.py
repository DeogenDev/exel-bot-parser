"""Незавасимая отправка сообщения"""

import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramRetryAfter, TelegramBadRequest

from src.shared import conf

logger = logging.getLogger(__name__)

bot = Bot(token=conf.bot.token)


async def send_telegram_message(
    chat_id: int,
    text: str,
    thread_id: int = None,
) -> None:

    while True:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=text,
                message_thread_id=thread_id,
            )

            await asyncio.sleep(1)
            return

        except TelegramRetryAfter as e:
            logger.warning(f"Flood control. Sleep {e.retry_after}s")
            await asyncio.sleep(e.retry_after)

        except TelegramBadRequest as e:
            logger.error(f"Bad request: {e}")
            return  # не ретраим

        except Exception as e:
            logger.exception(f"Unexpected telegram error: {e}")
            return