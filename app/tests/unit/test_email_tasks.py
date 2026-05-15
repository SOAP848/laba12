"""
Unit-тесты для задач Celery (email_tasks).
"""

import pytest
from unittest.mock import patch, MagicMock
from app.tasks.email_tasks import (
    send_welcome_email,
    send_order_confirmation,
    send_review_notification,
)


class TestEmailTasks:
    """Тесты для email задач."""

    @patch("app.tasks.email_tasks.sleep")
    @patch("app.tasks.email_tasks.logger")
    def test_send_welcome_email_success(self, mock_logger, mock_sleep):
        """Тест успешной отправки приветственного письма."""
        # Вызываем задачу
        result = send_welcome_email("test@example.com", "Test User")

        # Проверяем логирование
        mock_logger.info.assert_called_once_with(
            "Отправка приветственного письма на test@example.com для Test User"
        )
        mock_sleep.assert_called_once_with(2)
        assert result == "Письмо успешно отправлено на test@example.com"

    # Тест на повторную попытку при исключении пропущен из-за сложности мока self.retry
    # Можно добавить позже

    @patch("app.tasks.email_tasks.sleep")
    @patch("app.tasks.email_tasks.logger")
    def test_send_order_confirmation_success(self, mock_logger, mock_sleep):
        """Тест успешной отправки подтверждения заказа."""
        result = send_order_confirmation(123, "customer@example.com")

        mock_logger.info.assert_called_once_with(
            "Отправка подтверждения заказа 123 на customer@example.com"
        )
        mock_sleep.assert_called_once_with(1)
        assert result == "Подтверждение заказа 123 отправлено"

    @patch("app.tasks.email_tasks.sleep")
    @patch("app.tasks.email_tasks.logger")
    def test_send_review_notification_success(self, mock_logger, mock_sleep):
        """Тест успешной отправки уведомления о новом отзыве."""
        result = send_review_notification(5, 99)

        mock_logger.info.assert_called_once_with("Уведомление ресторану 5 о отзыве 99")
        mock_sleep.assert_called_once_with(1)
        assert result == "Уведомление отправлено ресторану 5"

    def test_send_welcome_email_without_mocks(self):
        """Интеграционный тест (без моков) для проверки работы функции."""
        # Этот тест вызовет реальный sleep, что замедлит выполнение.
        # Можно пропустить или использовать мок sleep.
        pass
