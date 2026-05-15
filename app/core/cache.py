import json
from typing import Any, Optional

import redis

from app.core.config import settings


class RedisCache:
    def __init__(self, url: str = settings.REDIS_URL):
        self.client = redis.from_url(url, decode_responses=True)

    def get(self, key: str) -> Optional[Any]:
        """Получить значение по ключу."""
        data = self.client.get(key)
        if data is None:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data

    def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """Установить значение с временем жизни в секундах."""
        data = json.dumps(value, default=str)
        self.client.setex(key, expire, data)

    def delete(self, key: str) -> None:
        """Удалить ключ."""
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Проверить существование ключа."""
        return self.client.exists(key) == 1

    def clear_pattern(self, pattern: str) -> None:
        """Удалить все ключи, соответствующие шаблону (через SCAN, без блокировки Redis)."""
        cursor = 0
        while True:
            cursor, keys = self.client.scan(cursor=cursor, match=pattern, count=100)
            if keys:
                self.client.delete(*keys)
            if cursor == 0:
                break


# Глобальный экземпляр кэша
cache = RedisCache()
