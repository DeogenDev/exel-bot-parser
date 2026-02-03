"""Приложение Celery."""

from celery import Celery
from src.shared import conf

app = Celery(
    "exel_bot_parser.celery_app",
    broker=f"amqp://{conf.rabbitmq.user}:{conf.rabbitmq.password}@rabbitmq:5672//",
    backend="rpc://",
    include=["src.celery_tasks.delete_message", "src.celery_tasks.transfer_messages"],
)
