"""Хендлер для получения сообщений."""

import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery


from src.service import MessageRedisStorage, MessageTransferService
from src.bot.keyboards import RETURN_TO_MENU_KEYBOARD

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "transfer_orders")
async def transfer_messages(
    callback: CallbackQuery,
    redis_client: MessageRedisStorage,
    message_transfer_service: MessageTransferService,
):
    """Хендлер вызова переноса сообщений."""
    try:
        await callback.answer()
        messages = await redis_client.get_all_messages()
        if not messages:
            await callback.message.edit_text(
                "🚫 В базе нет сообщений.", reply_markup=RETURN_TO_MENU_KEYBOARD
            )
            return
        await message_transfer_service.transfer_messages(callback.from_user.id)
        await callback.message.edit_text("📤 Переношу сообщения...")
    except Exception as e:
        logger.error(f"Failed to transfer messages: {e}")
