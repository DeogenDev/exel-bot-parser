"""Redis клиент для хранения и чтения айдишников."""

from redis.asyncio.client import Redis


class IdsRedisStorage:
    """
    Отвечает ТОЛЬКО за хранение и чтение айдишников.
    """

    def __init__(self, redis_client: Redis):
        self._redis = redis_client

    async def add_message_id(self, message_id: int) -> None:
        await self._add("message_ids", message_id)

    async def get_all_message_ids(self) -> list[int]:
        return await self._get_all("message_ids")

    async def remove_ids(self) -> list[int]:
        response = await self.get_all_message_ids()
        await self._redis.delete("message_ids")
        return response

    async def exists(self, key: str) -> bool:
        return await self._redis.exists(key) == 1

    async def _add(self, key: str, *ids: int) -> None:
        if not ids:
            return
        await self._redis.sadd(key, *ids)

    async def _get_all(self, key: str) -> list[int]:
        raw = await self._redis.smembers(key)
        return [int(i) for i in raw]
