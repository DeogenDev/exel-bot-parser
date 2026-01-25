"""Клавиатура меню бота."""

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


MENU_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📤 Перенести заказы", callback_data="transfer_orders"
            ),
            InlineKeyboardButton(text="🧹 Очистить чат", callback_data="clear_chat"),
        ],
        [InlineKeyboardButton(text="❔ Инфо ", callback_data="open_info")],
    ]
)

RETURN_TO_MENU_KEYBOARD = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="open_menu"),
        ],
    ]
)
