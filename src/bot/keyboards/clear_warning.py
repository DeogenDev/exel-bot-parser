"""Клавиатура меню бота."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


CLEAR_WARNING_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Назад", callback_data="open_menu"),
            InlineKeyboardButton(text="Очистить", callback_data="total_clear_chat"),
        ],
    ]
)
