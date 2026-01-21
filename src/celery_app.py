"""Приложение Celery."""

from celery import Celery


app = Celery(
    "exel_bot_parser.celery_app",
    broker="amqp://guest:guest@rabbitmq:5672/",
    backend="rpc://",
    include=["src.celery_tasks.delete_message"],
)
