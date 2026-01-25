"""Хендлеры бота"""

from .start import router as start_router
from .transfer_orders import router as transfer_orders_router
from .clear_chat import router as clear_chat_router
from .on_group_message import router as on_group_message_router
from .info import router as info_router

__all__ = (
    "start_router",
    "transfer_orders_router",
    "clear_chat_router",
    "on_group_message_router",
    "info_router",
)
