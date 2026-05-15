"""
Unit-тесты для задач Celery (email_tasks).
"""
import pytest
from unittest.mock import patch, MagicMock
from app.tasks.email_tasks import send_welcome_email, send_order_confirmation, send_review_notification


class TestEmailTasks:
    """Тесты для email задач."""

    @patch("app.tasks.email_tasks.sleep")
    @patch("app.tasks.email_tasks.logger")
    def test_send_welcome_email_success(self, mock_logger, mock_sleep):
        """Тест успешной отправки приветственного письма."""
        result = send_welcome_email("user@example.com", "John Doe")

        assert result == "Письмо успешно отправлено на user@example.com"
        mock_logger.info.assert_called()
        mock_sleep.assert_called_once_with(2)

    @patch("app.tasks.email_tasks.sleep")
    @patch("app.tasks.email_tasks.logger")
    def test_send_welcome_email_retry_on_exception(self, mock_logger, mock_sleep):
        """Тест повторной попытки при исключении."""
        mock_sleep.side_effect = Exception("Network error")
        task_mock = MagicMock()
        task_mock.retry = MagicMock()

        # Заменяем self на мок
        with patch.object(send_welcome_email, 'retry', task_mock.retry):
            with pytest.raises(Exception):
                send_welcome_email("user@example.com", "John Doe")

        mock_logger.error.assert_called()
        # Проверяем, что retry был вызван
        task_mock.retry.assert_called_once()

    @patch("app.tasks.email_tasks.sleep")
    @patch("app.tasks.email_tasks.logger")
    def test_send_order_confirmation_success(self, mock_logger, mock_sleep):
        """Тест успешной отправки подтверждения заказа."""
        result = send_order_confirmation(123, "customer@example.com")

        assert result == "Подтверждение заказа 123 отправлено"
        mock_logger.info.assert_called_with(
            "Отправка подтверждения заказа 123 на customer@example.com"
        )
        mock_sleep.assert_called_once_with(1)

    @patch("app.tasks.email_tasks.sleep")
    @patch("app.tasks.email_tasks.logger")
    def test_send_review_notification_success(self, mock_logger, mock_sleep):
        """Тест успешной отправки уведомления о новом отзыве."""
        result = send_review_notification(5, 99)

        assert result == "Уведомление отправлено ресторану 5"
        mock_logger.info.assert_called_with(
            "Уведомление ресторану 5 о отзыве 99"
        )
        mock_sleep.assert_called_once_with(1)

    def test_send_welcome_email_with_empty_email(self):
        """Тест отправки письма с пустым email (должно работать)."""
        # Задача не валидирует email, просто логирует.
        with patch("app.tasks.email_tasks.sleep"):
            with patch("app.tasks.email_tasks.logger"):
                result = send_welcome_email("", "No Name")
                assert "Письмо успешно отправлено на" in result

    def test_send_order_confirmation_with_zero_order_id(self):
        """Тест отправки подтверждения заказа с order_id = 0."""
        with patch("app.tasks.email_tasks.sleep"):
            with patch("app.tasks.email_tasks.logger"):
                result = send_order_confirmation(0, "test@example.com")
                assert "Подтверждение заказа 0 отправлено" in result

    def test_send_review_notification_with_negative_ids(self):
        """Тест отправки уведомления с отрицательными ID (должно работать)."""
        with patch("app.tasks.email_tasks.sleep"):
            with patch("app.tasks.email_tasks.logger"):
                result = send_review_notification(-1, -2)
                assert "Уведомление отправлено ресторану -1" in result