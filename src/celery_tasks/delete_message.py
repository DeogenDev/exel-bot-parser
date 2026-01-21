import asyncio
import logging

from aiogram import Bot

from src.shared import conf

from src.celery_app import app


logger = logging.getLogger(__name__)


@app.task(name="delete_messages_task", bind=True, queue="cleanup")
def delete_messages_task(self, message_ids: list[int]):
    """
    Асинхронное удаление сообщений через TG-бота.
    """
    logger.info(f"Deleting {len(message_ids)} messages")

    async def _delete():
        bot = Bot(token=conf.bot.token)
        int_chat_id = int(conf.bot.parse_channel_id)
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

    asyncio.run(_delete())
