"""Очистка чата."""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.service import MessageRedisStorage, MessageCleanupService
from src.bot.keyboards.menu import MENU_KEYBOARD


router = Router()


@router.callback_query(F.data == "clear_chat")
async def clear_chat(
    callback: CallbackQuery,
    redis_client: MessageRedisStorage,
    message_cleanup_service: MessageCleanupService,
):
    await callback.answer()
    ids = await redis_client.get_all_message_ids()
    if not ids:
        await callback.message.answer(
            "🚫 В базе нет сообщений.", reply_markup=MENU_KEYBOARD
        )
        return
    await message_cleanup_service.remove_all_messages()
    await callback.message.answer("🧹 Очищаю чат...")
