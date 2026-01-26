"""Хендлер старта у бота."""

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

from src.bot.keyboards import MENU_KEYBOARD

router = Router()


menu_text = "🛂 Бот для переноса заказов в exel таблицу.\nВыберите действие:"


@router.message(CommandStart(), F.message.chat.type == "private")
async def start(message: Message):
    await message.answer(
        menu_text,
        reply_markup=MENU_KEYBOARD,
        parse_mode="HTML",
    )


@router.callback_query(F.data == "open_menu")
async def open_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        menu_text,
        reply_markup=MENU_KEYBOARD,
        parse_mode="HTML",
    )
