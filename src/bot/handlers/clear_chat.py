"""Очистка чата."""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.service import MessageRedisStorage, MessageCleanupService
from src.bot.keyboards import (
    CLEAR_WARNING_KEYBOARD,
    RETURN_TO_MENU_KEYBOARD,
)


router = Router()


warning_text = (
    "⚠️ **ПОДТВЕРЖДЕНИЕ ОЧИСТКИ**\n\n"
    "Перед продолжением проверьте следующее:\n"
    "1️⃣ Данные перенесены в таблицу.\n"
    "2️⃣ Сообщения в чате больше не нужны.\n\n"
    "❗ **Действие необратимо.** Нажав кнопку, вы удалите историю сообщений навсегда."
)


@router.callback_query(F.data == "clear_chat")
async def clear_chat(
    callback: CallbackQuery,
    redis_client: MessageRedisStorage,
):
    await callback.answer()
    ids = await redis_client.get_all_message_ids()
    if not ids:
        await callback.message.edit_text(
            "🚫 В базе нет сообщений.",
            reply_markup=RETURN_TO_MENU_KEYBOARD,
        )
        return
    await callback.message.edit_text(
        text=warning_text,
        reply_markup=CLEAR_WARNING_KEYBOARD,
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "total_clear_chat")
async def total_clear_chat(
    callback: CallbackQuery,
    message_cleanup_service: MessageCleanupService,
):
    await callback.message.delete_reply_markup()
    await message_cleanup_service.remove_all_messages(user_id=callback.from_user.id)
    await callback.message.answer("🧹 Очищаю чат...")
