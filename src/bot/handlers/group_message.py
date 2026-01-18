"""Хендлер для получения сообщений."""

import logging
from aiogram import Router, F
from aiogram.types import Message

from src.utils.text_extractor import TextExtractor

extractor = TextExtractor()

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def handle_group_text(message: Message):
    """Обработка текстовых сообщений."""
    # logger.info("Received text message: %s", message.text)
    print(extractor.extract_message(message.text))
