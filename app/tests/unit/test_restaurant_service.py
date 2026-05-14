import pytest
from sqlalchemy.orm import Session
from unittest.mock import Mock, patch

from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate
from app.services.restaurant_service import RestaurantService


class TestRestaurantService:
    """Тесты для RestaurantService."""

    @pytest.fixture
    def mock_db(self):
        return Mock(spec=Session)

    @pytest.fixture
    def sample_restaurant(self):
        # Возвращаем мок, чтобы избежать проблем с инициализацией SQLAlchemy мапперов
        mock = Mock(spec=Restaurant)
        mock.id = 1
        mock.name = "Test Restaurant"
        mock.description = "Test description"
        mock.address = "Test address"
        mock.phone = "+79991234567"
        mock.email = "test@example.com"
        mock.delivery_fee = 100.0
        mock.min_order_amount = 500.0
        mock.delivery_time_min = 30
        mock.delivery_time_max = 60
        mock.is_active = True
        return mock

    def test_get_all(self, mock_db):
        """Получение списка ресторанов."""
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.count.return_value = 2
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [Mock(), Mock()]

        restaurants, total = RestaurantService.get_all(
            mock_db, skip=0, limit=20, is_active=True
        )
        assert total == 2
        assert len(restaurants) == 2
        mock_db.query.assert_called_once_with(Restaurant)
        mock_query.filter.assert_called_once_with(Restaurant.is_active == True)

    def test_get_by_id(self, mock_db):
        """Получение ресторана по ID."""
        mock_db.query.return_value.get.return_value = Mock()
        result = RestaurantService.get_by_id(mock_db, 1)
        assert result is not None
        mock_db.query.assert_called_once_with(Restaurant)

    @patch('app.services.restaurant_service.Restaurant')
    def test_create(self, mock_restaurant_cls, mock_db):
        """Создание ресторана."""
        restaurant_data = RestaurantCreate(
            name="New Restaurant",
            description="New description",
            address="New address",
            phone="+79991234567",
            email="new@example.com",
            delivery_fee=150.0,
            min_order_amount=600.0,
            delivery_time_min=40,
            delivery_time_max=80,
            is_active=True,
        )
        mock_restaurant = Mock()
        mock_restaurant_cls.return_value = mock_restaurant
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        result = RestaurantService.create(mock_db, restaurant_data)
        assert result is mock_restaurant
        mock_restaurant_cls.assert_called_once_with(**restaurant_data.model_dump())
        mock_db.add.assert_called_once_with(mock_restaurant)
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_restaurant)

    def test_update(self, mock_db, sample_restaurant):
        """Обновление ресторана."""
        update_data = RestaurantUpdate(delivery_fee=200.0)
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        result = RestaurantService.update(mock_db, sample_restaurant, update_data)
        assert result.delivery_fee == 200.0
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

    def test_delete(self, mock_db, sample_restaurant):
        """Удаление ресторана."""
        mock_db.delete = Mock()
        mock_db.commit = Mock()

        RestaurantService.delete(mock_db, sample_restaurant)
        mock_db.delete.assert_called_once_with(sample_restaurant)
        mock_db.commit.assert_called_once()

    def test_toggle_active(self, mock_db, sample_restaurant):
        """Активация/деактивация ресторана."""
        mock_db.commit = Mock()
        mock_db.refresh = Mock()

        result = RestaurantService.toggle_active(mock_db, sample_restaurant, False)
        assert result.is_active is False
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
