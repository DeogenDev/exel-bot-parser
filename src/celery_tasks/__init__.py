"""Задачи Celery."""

from .delete_message import delete_messages_task
from .transfer_messages import transfer_message_task

__all__ = (
    "delete_messages_task",
    "transfer_message_task",
)
