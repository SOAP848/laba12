import logging
from time import sleep

from app.core.celery import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def send_welcome_email(self, user_email: str, user_name: str) -> str:
    """
    Пример задачи отправки приветственного email.
    В реальном приложении здесь будет интеграция с почтовым сервисом.
    """
    try:
        # Имитация отправки email
        logger.info(f"Отправка приветственного письма на {user_email} для {user_name}")
        sleep(2)  # Имитация задержки
        # В реальности: send_email(...)
        return f"Письмо успешно отправлено на {user_email}"
    except Exception as exc:
        logger.error(f"Ошибка отправки письма: {exc}")
        raise self.retry(exc=exc, countdown=60)


@celery_app.task
def send_order_confirmation(order_id: int, customer_email: str) -> str:
    """
    Отправка подтверждения заказа.
    """
    logger.info(f"Отправка подтверждения заказа {order_id} на {customer_email}")
    sleep(1)
    return f"Подтверждение заказа {order_id} отправлено"


@celery_app.task
def send_review_notification(restaurant_id: int, review_id: int) -> str:
    """
    Уведомление ресторану о новом отзыве.
    """
    logger.info(f"Уведомление ресторану {restaurant_id} о отзыве {review_id}")
    sleep(1)
    return f"Уведомление отправлено ресторану {restaurant_id}"
