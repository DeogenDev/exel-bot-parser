"""Информация о боте."""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.shared import conf
from src.bot.keyboards import RETURN_TO_MENU_KEYBOARD


router = Router()

INFO_TEXT = (
    f"❔ Информация о боте:\n\n"
    f"<b>ID таблицы:</b> {conf.google.spreadsheet_id}\n"
    f"<b>Имя листа:</b> {conf.google.sheet_name}\n"
    f"<b>ID группы:</b> {conf.bot.parse_channel_id}\n"
)


@router.callback_query(F.data == "open_info")
async def open_info(callback: CallbackQuery):
    await callback.message.edit_text(
        text=INFO_TEXT,
        reply_markup=RETURN_TO_MENU_KEYBOARD,
        parse_mode="HTML",
    )
