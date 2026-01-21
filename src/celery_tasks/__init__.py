"""Задачи Celery."""

from .delete_message import delete_messages_task

__all__ = ("delete_messages_task",)
