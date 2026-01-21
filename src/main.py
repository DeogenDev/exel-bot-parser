"""Файл запуска."""

import logging
import asyncio


from src.utils import message_parser_bot

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    await message_parser_bot.run()


if __name__ == "__main__":
    asyncio.run(main())

    logger.info("Bot stopped")
