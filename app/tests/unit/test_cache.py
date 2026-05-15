import pytest
from unittest.mock import Mock, patch

from app.core.cache import RedisCache


class TestRedisCache:
    """Тесты для RedisCache."""

    @pytest.fixture
    def mock_redis_client(self):
        with patch("redis.from_url") as mock_from_url:
            mock_client = Mock()
            mock_from_url.return_value = mock_client
            yield mock_client

    def test_get_json(self, mock_redis_client):
        """Получение значения, сериализованного JSON."""
        cache = RedisCache(url="redis://localhost:6379/0")
        mock_redis_client.get.return_value = '{"foo": "bar"}'
        result = cache.get("test_key")
        assert result == {"foo": "bar"}

    def test_get_string(self, mock_redis_client):
        """Получение невалидного JSON как строки."""
        cache = RedisCache()
        mock_redis_client.get.return_value = "plain string"
        result = cache.get("test_key")
        assert result == "plain string"

    def test_get_none(self, mock_redis_client):
        """Получение отсутствующего ключа."""
        cache = RedisCache()
        mock_redis_client.get.return_value = None
        result = cache.get("test_key")
        assert result is None

    def test_set_json(self, mock_redis_client):
        """Установка значения с JSON сериализацией."""
        cache = RedisCache()
        cache.set("key", {"simple": "object"})
        mock_redis_client.setex.assert_called_once_with(
            "key", 3600, '{"simple": "object"}'
        )

    def test_set_non_serializable(self, mock_redis_client):
        """Установка значения с default=str для несериализуемых типов."""
        cache = RedisCache()
        from datetime import datetime

        cache.set("key", datetime(2024, 1, 1))
        call_args = mock_redis_client.setex.call_args[0]
        assert call_args[0] == "key"
        assert call_args[1] == 3600
        assert "2024-01-01" in call_args[2]

    def test_delete(self, mock_redis_client):
        """Удаление ключа."""
        cache = RedisCache()
        cache.delete("key")
        mock_redis_client.delete.assert_called_once_with("key")

    def test_exists(self, mock_redis_client):
        """Проверка существования ключа."""
        cache = RedisCache()
        mock_redis_client.exists.return_value = 1
        assert cache.exists("key") is True
        mock_redis_client.exists.return_value = 0
        assert cache.exists("key") is False

    def test_clear_pattern(self, mock_redis_client):
        """Очистка по шаблону через SCAN."""
        cache = RedisCache()
        mock_redis_client.scan.side_effect = [(1, ["key1", "key2"]), (0, [])]
        cache.clear_pattern("pattern*")
        mock_redis_client.scan.assert_called()
        mock_redis_client.delete.assert_called_once_with("key1", "key2")

    def test_clear_pattern_no_keys(self, mock_redis_client):
        """Очистка по шаблону, когда ключей нет."""
        cache = RedisCache()
        mock_redis_client.scan.return_value = (0, [])
        cache.clear_pattern("pattern*")
        mock_redis_client.delete.assert_not_called()
