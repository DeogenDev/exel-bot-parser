from redis.asyncio.client import Redis

from src.shared import conf
from src.service import (
    MessageRedisStorage,
    MessageCleanupService,
    MessageTransferService,
    TableManager,
)
from src.bot import MessageParserBot
from src.celery_tasks import delete_messages_task, transfer_message_task

table_manager = TableManager(
    credentials=conf.google.credentials_path,
    spreadsheet_id=conf.google.spreadsheet_id,
    sheet_name=conf.google.sheet_name,
)


redis_client = MessageRedisStorage(
    redis_client=Redis(
        host=conf.redis.host,
        port=conf.redis.port,
        decode_responses=True,
    ),
    chat_id=conf.bot.parse_channel_id,
)

message_cleanup_service = MessageCleanupService(
    storage=redis_client,
    delete_messages_task=delete_messages_task,
)

message_transfer_service = MessageTransferService(
    storage=redis_client,
    transfer_messages_task=transfer_message_task,
)

message_parser_bot = MessageParserBot(
    token=conf.bot.token,
    parse_channel_id=conf.bot.parse_channel_id,
    redis_client=redis_client,
    message_cleanup_service=message_cleanup_service,
    message_transfer_service=message_transfer_service,
)
