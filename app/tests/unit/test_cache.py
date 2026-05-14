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

    def test_get_pickle(self, mock_redis_client):
        """Получение значения, сериализованного pickle."""
        cache = RedisCache(url="redis://localhost:6379/0")
        mock_redis_client.get.return_value = b"pickled_data"
        with patch("pickle.loads", return_value={"foo": "bar"}) as mock_loads:
            result = cache.get("test_key")
            mock_loads.assert_called_once_with(b"pickled_data")
            assert result == {"foo": "bar"}

    def test_get_json(self, mock_redis_client):
        """Получение значения, сериализованного JSON."""
        cache = RedisCache()
        mock_redis_client.get.return_value = b'{"foo": "bar"}'
        result = cache.get("test_key")
        assert result == {"foo": "bar"}

    def test_get_string(self, mock_redis_client):
        """Получение строкового значения."""
        cache = RedisCache()
        mock_redis_client.get.return_value = b"plain string"
        result = cache.get("test_key")
        assert result == "plain string"

    def test_get_none(self, mock_redis_client):
        """Получение отсутствующего ключа."""
        cache = RedisCache()
        mock_redis_client.get.return_value = None
        result = cache.get("test_key")
        assert result is None

    def test_set_pickle(self, mock_redis_client):
        """Установка значения с pickle сериализацией."""
        cache = RedisCache()
        with patch("pickle.dumps", return_value=b"pickled") as mock_dumps:
            cache.set("key", {"complex": "object"})
            mock_dumps.assert_called_once_with({"complex": "object"})
            mock_redis_client.setex.assert_called_once_with("key", 3600, b"pickled")

    def test_set_json(self, mock_redis_client):
        """Установка значения с JSON сериализацией (если pickle падает)."""
        cache = RedisCache()
        with patch("pickle.dumps", side_effect=Exception("Cannot pickle")):
            with patch("json.dumps", return_value='{"simple": "object"}') as mock_json:
                cache.set("key", {"simple": "object"})
                mock_json.assert_called_once_with({"simple": "object"})
                mock_redis_client.setex.assert_called_once_with(
                    "key", 3600, b'{"simple": "object"}'
                )

    def test_set_string(self, mock_redis_client):
        """Установка строкового значения (если и pickle, и JSON падают)."""
        cache = RedisCache()
        with patch("pickle.dumps", side_effect=Exception("Cannot pickle")):
            with patch("json.dumps", side_effect=Exception("Cannot json")):
                cache.set("key", "plain string")
                mock_redis_client.setex.assert_called_once_with(
                    "key", 3600, b"plain string"
                )

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
        """Очистка по шаблону."""
        cache = RedisCache()
        mock_redis_client.keys.return_value = [b"key1", b"key2"]
        cache.clear_pattern("pattern*")
        mock_redis_client.keys.assert_called_once_with("pattern*")
        mock_redis_client.delete.assert_called_once_with(b"key1", b"key2")

    def test_clear_pattern_no_keys(self, mock_redis_client):
        """Очистка по шаблону, когда ключей нет."""
        cache = RedisCache()
        mock_redis_client.keys.return_value = []
        cache.clear_pattern("pattern*")
        mock_redis_client.keys.assert_called_once_with("pattern*")
        mock_redis_client.delete.assert_not_called()
