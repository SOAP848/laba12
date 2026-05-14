import json
import pickle
from typing import Any, Optional

import redis
from pydantic import BaseSettings

from app.core.config import settings


class RedisCache:
    def __init__(self, url: str = settings.REDIS_URL):
        self.client = redis.from_url(url, decode_responses=False)

    def get(self, key: str) -> Optional[Any]:
        """Получить значение по ключу."""
        data = self.client.get(key)
        if data is None:
            return None
        try:
            return pickle.loads(data)
        except pickle.UnpicklingError:
            # Если не сериализовано pickle, попробуем как JSON строку
            try:
                return json.loads(data.decode())
            except (json.JSONDecodeError, UnicodeDecodeError):
                return data.decode()

    def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """Установить значение с временем жизни в секундах."""
        try:
            data = pickle.dumps(value)
        except Exception:
            # Если не сериализуется pickle, попробуем JSON
            try:
                data = json.dumps(value).encode()
            except Exception:
                data = str(value).encode()
        self.client.setex(key, expire, data)

    def delete(self, key: str) -> None:
        """Удалить ключ."""
        self.client.delete(key)

    def exists(self, key: str) -> bool:
        """Проверить существование ключа."""
        return self.client.exists(key) == 1

    def clear_pattern(self, pattern: str) -> None:
        """Удалить все ключи, соответствующие шаблону."""
        keys = self.client.keys(pattern)
        if keys:
            self.client.delete(*keys)


# Глобальный экземпляр кэша
cache = RedisCache()
