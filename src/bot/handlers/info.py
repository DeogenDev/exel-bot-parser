"""Информация о боте."""

from aiogram import Router, F
from aiogram.types import CallbackQuery

from src.shared import conf
from src.bot.keyboards import RETURN_TO_MENU_KEYBOARD

from src.service import MessageRedisStorage


router = Router()

INFO_TEXT_TEMPLATE = """
❔ <b>Информация</b>

========== Exel ==========
<b>ID таблицы:</b> {spreadsheet_id}
<b>Имя листа:</b> {sheet_name}

======== Telegram =========
<b>ID группы:</b> {parse_channel_id}
<b>ID темы логов:</b> {logs_topic_id}
<b>ID темы парсинга:</b> {parse_topic_id}

========== Redis ==========
<b>Сообщений в базе:</b> {message_count}
"""


@router.callback_query(F.data == "open_info")
async def open_info(
    callback: CallbackQuery,
    redis_client: MessageRedisStorage,
):
    messages = await redis_client.get_all_messages()

    text = INFO_TEXT_TEMPLATE.format(
        spreadsheet_id=conf.google.spreadsheet_id,
        sheet_name=conf.google.sheet_name,
        parse_channel_id=conf.bot.parse_channel_id,
        logs_topic_id=conf.bot.logs_topic_id,
        parse_topic_id=conf.bot.parse_topic_id,
        message_count=len(messages),
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=RETURN_TO_MENU_KEYBOARD.f,
        parse_mode="HTML",
    )
