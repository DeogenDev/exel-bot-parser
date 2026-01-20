""""""

from celery import Celery


app = Celery(
    "exel_bot_parser.service.celery",
    broker="amqp://guest:guest@localhost:5672/",
    backend="rpc://",
)
