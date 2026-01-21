from redis.asyncio.client import Redis

from src.shared import conf
from src.service import IdsRedisStorage, MessageCleanupService
from src.utils import messages_extractor
from src.bot import MessageParserBot
from src.celery_tasks import delete_messages_task


redis_client = IdsRedisStorage(
    redis_client=Redis(
        host=conf.redis.host,
        port=conf.redis.port,
        decode_responses=True,
    )
)

message_cleanup_service = MessageCleanupService(
    redis_client,
    delete_messages_task,
)


message_parser_bot = MessageParserBot(
    token=conf.bot.token,
    parse_channel_id=conf.bot.parse_channel_id,
    messages_extractor=messages_extractor,
    redis_client=redis_client,
    message_cleanup_service=message_cleanup_service,
)
