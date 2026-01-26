"""При получении сообщений в группе."""

import logging

from aiogram import Router, F
from aiogram.types import Message

from src.service import MessageRedisStorage

logger = logging.getLogger(__name__)
router = Router()


async def save_group_message(
    message: Message,
    parsing_chat_id: str,
    redis_client: MessageRedisStorage,
    parse_topic_id: int,
):
    """Сохраняет текст сообщения в Redis, проверяя chat_id."""
    if (
        message.chat.id != int(parsing_chat_id)
        and message.message_thread_id != parse_topic_id
    ):
        return
    if not message.text:
        return
    await redis_client.save_message(message.message_id, message.text)
    logger.info("Saved message ID: %s", message.message_id)


@router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def handle_group_text(
    message: Message,
    parsing_chat_id: str,
    redis_client: MessageRedisStorage,
    parse_topic_id: int,
):
    await save_group_message(
        message,
        parsing_chat_id,
        redis_client,
        parse_topic_id,
    )


@router.edited_message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def handle_edited_group_text(
    message: Message,
    parsing_chat_id: str,
    redis_client: MessageRedisStorage,
    parse_topic_id: int,
):
    await save_group_message(
        message,
        parsing_chat_id,
        redis_client,
        parse_topic_id,
    )
