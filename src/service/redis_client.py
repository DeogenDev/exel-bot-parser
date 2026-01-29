"""Redis клиент для хранения и чтения айдишников."""

from redis.asyncio.client import Redis


SAVE_MESSAGE_LUA = """
if redis.call('HEXISTS', KEYS[1], ARGV[1]) == 0 then
    redis.call('RPUSH', KEYS[2], ARGV[1])
end
redis.call('HSET', KEYS[1], ARGV[1], ARGV[2])
return 1
"""


class MessageRedisStorage:
    """
    Хранилище сообщений Telegram с сохранением порядка вставки.
    """

    def __init__(self, redis_client: Redis, chat_id: int) -> None:
        self._redis = redis_client
        self._key = f"chat:{chat_id}:messages"
        self._save_message = self._redis.register_script(SAVE_MESSAGE_LUA)

    async def save_message(self, message_id: int, text: str) -> None:
        await self._save_message(
            keys=[self._key, f"{self._key}:order"],
            args=[message_id, text],
        )

    async def get_all_messages(self) -> dict[int, str]:
        ids = await self._redis.lrange(f"{self._key}:order", 0, -1)
        if not ids:
            return {}

        values = await self._redis.hmget(self._key, *ids)

        return {int(mid): text for mid, text in zip(ids, values) if text is not None}

    async def remove_all_messages(self) -> list[int]:
        ids = await self._redis.lrange(f"{self._key}:order", 0, -1)

        if ids:
            await self._redis.delete(
                self._key,
                f"{self._key}:order",
            )

        return [int(i) for i in ids]

    async def get_all_message_ids(self) -> list[int]:
        """
        Возвращает message_id в порядке их добавления.
        """
        ids = await self._redis.lrange(f"{self._key}:order", 0, -1)
        return [int(mid) for mid in ids]
