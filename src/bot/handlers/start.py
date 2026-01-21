"""Хендлер старта у бота."""

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from src.bot.keyboards import MENU_KEYBOARD

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет, я бот для переноса заказов", reply_markup=MENU_KEYBOARD
    )
