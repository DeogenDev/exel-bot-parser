"""При получении сообщений в группе."""

import logging

from aiogram import Router, F
from aiogram.types import Message

from src.service import IdsRedisStorage

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def handle_group_text(
    message: Message,
    parsing_chat_id: str,
    redis_client: IdsRedisStorage,
):
    """Обработка текстовых сообщений."""
    if message.chat.id != int(parsing_chat_id):
        logger.info("Received message from unknown chat: %s", message.chat.username)
        return
    await redis_client.add_message_id(message.message_id)
    logger.info("Saved message ID: %s", message.message_id)
