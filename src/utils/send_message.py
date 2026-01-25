from aiogram import Bot


async def send_telegram_message(token, chat_id, text):
    async with Bot(token=token).context() as bot:
        await bot.send_message(chat_id=chat_id, text=text)
