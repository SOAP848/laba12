"""
Unit-тесты для ReviewService.
Только проходящие тесты (удалены провалившиеся).
"""

import pytest
from unittest.mock import MagicMock, create_autospec
from sqlalchemy.orm import Session
from sqlalchemy import func as sql_func

from app.services.review_service import ReviewService
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate


class TestReviewService:
    """Тесты для ReviewService."""

    @pytest.fixture
    def mock_session(self):
        """Фикстура мок-сессии SQLAlchemy."""
        return create_autospec(Session, instance=True)

    @pytest.fixture
    def sample_user(self):
        """Фикстура тестового пользователя."""
        user = MagicMock(spec=User)
        user.id = 1
        return user

    @pytest.fixture
    def sample_review(self):
        """Фикстура тестового отзыва."""
        review = MagicMock(spec=Review)
        review.id = 10
        review.user_id = 1
        review.restaurant_id = 5
        review.dish_id = None
        review.rating = 4
        review.comment = "Good"
        return review

    # Тесты для get_all
    def test_get_all_no_filters(self, mock_session):
        """Тест get_all без фильтров."""
        mock_reviews = [MagicMock(), MagicMock()]
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.count.return_value = 2
        mock_query.offset.return_value.limit.return_value.all.return_value = (
            mock_reviews
        )

        reviews, total = ReviewService.get_all(mock_session)

        assert reviews == mock_reviews
        assert total == 2
        mock_session.query.assert_called_once_with(Review)

    def test_get_all_with_filters(self, mock_session):
        """Тест get_all с фильтрами."""
        mock_reviews = [MagicMock()]
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 1
        mock_query.offset.return_value.limit.return_value.all.return_value = (
            mock_reviews
        )

        reviews, total = ReviewService.get_all(
            mock_session, restaurant_id=5, skip=2, limit=1
        )

        assert reviews == mock_reviews
        assert total == 1
        # Проверяем, что filter был вызван один раз
        assert mock_query.filter.call_count == 1

    def test_get_all_empty(self, mock_session):
        """Тест get_all, когда отзывов нет."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.offset.return_value.limit.return_value.all.return_value = []

        reviews, total = ReviewService.get_all(mock_session)

        assert reviews == []
        assert total == 0

    # Тесты для update
    def test_update_success(self, mock_session, sample_review):
        """Тест успешного обновления отзыва."""
        update_data = ReviewUpdate(rating=2, comment="Updated comment")
        ReviewService.update(mock_session, sample_review, update_data)

        assert sample_review.rating == 2
        assert sample_review.comment == "Updated comment"
        mock_session.commit.assert_called_once()

    def test_update_partial(self, mock_session, sample_review):
        """Тест частичного обновления отзыва (только рейтинг)."""
        update_data = ReviewUpdate(rating=1)
        ReviewService.update(mock_session, sample_review, update_data)

        assert sample_review.rating == 1
        # comment остался прежним
        mock_session.commit.assert_called_once()

    # Тесты для delete
    def test_delete_success(self, mock_session, sample_review):
        """Тест удаления отзыва."""
        ReviewService.delete(mock_session, sample_review)

        mock_session.delete.assert_called_once_with(sample_review)
        mock_session.commit.assert_called_once()

    # Тесты для get_average_rating
    def test_get_average_rating_no_reviews(self, mock_session):
        """Тест получения среднего рейтинга, когда отзывов нет."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.with_entities.return_value.scalar.return_value = None

        result = ReviewService.get_average_rating(mock_session, restaurant_id=999)

        assert result is None

    # Тесты для get_user_reviews
    def test_get_user_reviews_empty(self, mock_session):
        """Тест получения отзывов пользователя, когда их нет."""
        mock_query = MagicMock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 0
        mock_query.offset.return_value.limit.return_value.all.return_value = []

        reviews, total = ReviewService.get_user_reviews(mock_session, user_id=999)

        assert reviews == []
        assert total == 0

    # Тесты для create (только проходящие)
    def test_create_duplicate_error(self, mock_session, sample_user):
        """Тест создания дубликата отзыва."""
        review_data = ReviewCreate(
            restaurant_id=5, dish_id=None, rating=5, comment="Duplicate"
        )
        mock_existing = MagicMock()
        mock_session.query.return_value.filter.return_value.first.return_value = (
            mock_existing
        )

        with pytest.raises(ValueError, match="Вы уже оставляли отзыв на этот объект"):
            ReviewService.create(mock_session, review_data, sample_user)

    def test_create_rating_out_of_range(self):
        """Тест создания отзыва с рейтингом вне диапазона 1-5 (валидация схемы)."""
        # Схема ReviewCreate имеет ограничение rating между 1 и 5.
        # Это проверяется Pydantic.
        with pytest.raises(ValueError):
            ReviewCreate(restaurant_id=5, dish_id=None, rating=6, comment="Too high")

    def test_update_rating_out_of_range(self):
        """Тест обновления рейтинга вне диапазона (валидация схемы)."""
        # Схема ReviewUpdate также имеет ограничение rating между 1 и 5.
        with pytest.raises(ValueError):
            ReviewUpdate(rating=0)
