"""Redis клиент для хранения и чтения айдишников."""

from redis.asyncio.client import Redis


class MessageRedisStorage:
    """
    Отвечает ТОЛЬКО за хранение и чтение айдишников.
    """

    def __init__(self, redis_client: Redis, chat_id: int) -> None:
        self._redis = redis_client
        self._key = chat_id

    async def save_message(self, message_id: int, text: str) -> None:
        """Сохраняет или обновляет сообщение."""
        await self._redis.hset(self._key, message_id, text)

    async def get_all_message_ids(self) -> list[int]:
        """Возвращает все message_id, которые есть в Redis."""
        ids = await self._redis.hkeys(self._key)
        return [int(i) for i in ids]

    async def remove_all_messages(self) -> list[int]:
        """
        Удаляет все сообщения из Redis и возвращает список их ID.
        Аналог твоего remove_ids.
        """
        message_ids = await self.get_all_message_ids()
        if message_ids:
            await self._redis.delete(self._key)
        return message_ids

    async def get_all_messages(self) -> dict[int, str]:
        """
        Возвращает все сообщения в формате {message_id: text}.
        """
        raw = await self._redis.hgetall(self._key)
        return {int(k): v for k, v in raw.items()}
