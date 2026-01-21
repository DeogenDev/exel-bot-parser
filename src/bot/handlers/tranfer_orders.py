"""Хендлер для получения сообщений."""

import logging
from aiogram import Router, F
from aiogram.types import Message, ChatFullInfo

from src.utils import MessageExtractor, MessageExtractError, MessageExtractNoName
from src.models import HorizontalProductLine

from src.service import CharComparator

logger = logging.getLogger(__name__)
router = Router()


# @router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
# async def handle_group_text(
#     message: Message, parsing_chat_id: str, messages_extractor: MessageExtractor
# ):
#     """Обработка текстовых сообщений."""
#     if message.chat.id != int(parsing_chat_id):
#         logger.info("Received message from unknown chat: %s", message.chat.username)
#         return

#     try:
#         await message.bot.get_chat
#         # Извлекаем продукты из сообщения
#         extract_message = messages_extractor.extract_message(message.text)
#         logger.info("Extracted message: %s", extract_message)

#     except MessageExtractNoName as e:
#         logger.info("Message extraction skipped: %s", e)
#     except MessageExtractError as e:
#         logger.error("Message extraction error: %s", e)
