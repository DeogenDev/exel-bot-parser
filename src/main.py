"""Файл запуска."""

import logging
import asyncio

from src.shared import conf
from src.bot import MessageParserBot

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


message_parser_bot = MessageParserBot(
    token=conf.bot.token, parse_channel_id=conf.bot.parse_channel_id
)


async def main():
    await message_parser_bot.run()


if __name__ == "__main__":
    asyncio.run(main())

    logger.info("Bot stopped")
