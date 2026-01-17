"""Хендлер для получения сообщений."""

import logging
from aiogram import Router, F
from aiogram.types import Message

logger = logging.getLogger(__name__)
router = Router()


@router.message(F.chat.type.in_({"group", "supergroup"}), F.text)
async def handle_group_text(message: Message):
    chat_id = message.chat.id
    if message.chat.id != chat_id:
        return
