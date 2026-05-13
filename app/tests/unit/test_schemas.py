import pytest
from pydantic import ValidationError
from datetime import datetime

from app.schemas.user import UserCreate, UserUpdate, UserRole
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate
from app.schemas.dish import DishCreate, DishUpdate, DishCategory
from app.schemas.order import OrderCreate, OrderItemCreate, OrderStatus, PaymentMethod
from app.schemas.favorite import FavoriteCreate
from app.schemas.review import ReviewCreate


class TestUserSchemas:
    def test_user_create_valid(self):
        """Тест создания пользователя с валидными данными."""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "phone_number": "+79123456789",
            "address": "Test Address",
            "password": "Password123",
        }
        user = UserCreate(**data)
        assert user.email == data["email"]
        assert user.username == data["username"]
        assert user.password == data["password"]

    def test_user_create_invalid_email(self):
        """Тест с невалидным email."""
        data = {
            "email": "invalid-email",
            "username": "testuser",
            "password": "Password123",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_short_password(self):
        """Тест с коротким паролем."""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "short",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_password_no_uppercase(self):
        """Тест пароля без заглавной буквы."""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "password123",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_create_password_no_digit(self):
        """Тест пароля без цифры."""
        data = {
            "email": "test@example.com",
            "username": "testuser",
            "password": "Password",
        }
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_user_update_partial(self):
        """Тест частичного обновления пользователя."""
        data = {"email": "new@example.com"}
        user = UserUpdate(**data)
        assert user.email == "new@example.com"
        assert user.username is None


class TestRestaurantSchemas:
    def test_restaurant_create_valid(self):
        """Тест создания ресторана с валидными данными."""
        data = {
            "name": "Test Restaurant",
            "description": "A test restaurant",
            "address": "Test Street 123",
            "phone": "+79123456789",
            "delivery_time_min": 30,
            "delivery_fee": 100.0,
            "min_order_amount": 500.0,
        }
        restaurant = RestaurantCreate(**data)
        assert restaurant.name == data["name"]
        assert restaurant.delivery_fee == 100.0

    def test_restaurant_create_negative_delivery_fee(self):
        """Тест с отрицательной платой за доставку."""
        data = {"name": "Test", "address": "Address", "delivery_fee": -10.0}
        with pytest.raises(ValidationError):
            RestaurantCreate(**data)

    def test_restaurant_create_delivery_time_too_small(self):
        """Тест со слишком малым временем доставки."""
        data = {
            "name": "Test",
            "address": "Address",
            "delivery_time_min": 0,  # меньше минимального (5)
        }
        with pytest.raises(ValidationError):
            RestaurantCreate(**data)

    def test_restaurant_create_delivery_time_too_large(self):
        """Тест со слишком большим временем доставки."""
        data = {
            "name": "Test",
            "address": "Address",
            "delivery_time_min": 200,  # больше максимального (180)
        }
        with pytest.raises(ValidationError):
            RestaurantCreate(**data)


class TestDishSchemas:
    def test_dish_create_valid(self):
        """Тест создания блюда с валидными данными."""
        data = {
            "restaurant_id": 1,
            "name": "Test Dish",
            "description": "A test dish",
            "price": 350.0,
            "category": DishCategory.MAIN,
            "calories": 500,
            "cooking_time_min": 20,
        }
        dish = DishCreate(**data)
        assert dish.name == data["name"]
        assert dish.price == 350.0
        assert dish.category == DishCategory.MAIN

    def test_dish_create_price_zero(self):
        """Тест с нулевой ценой."""
        data = {"restaurant_id": 1, "name": "Test Dish", "price": 0.0}
        with pytest.raises(ValidationError):
            DishCreate(**data)  # gt=0, поэтому 0 недопустимо

    def test_dish_create_price_negative(self):
        """Тест с отрицательной ценой."""
        data = {"restaurant_id": 1, "name": "Test Dish", "price": -10.0}
        with pytest.raises(ValidationError):
            DishCreate(**data)

    def test_dish_create_price_too_high(self):
        """Тест со слишком высокой ценой."""
        data = {
            "restaurant_id": 1,
            "name": "Test Dish",
            "price": 20000.0,  # больше максимального (10000)
        }
        with pytest.raises(ValidationError):
            DishCreate(**data)

    def test_dish_create_cooking_time_invalid(self):
        """Тест с невалидным временем приготовления."""
        data = {
            "restaurant_id": 1,
            "name": "Test Dish",
            "price": 100.0,
            "cooking_time_min": 0,  # меньше минимального (1)
        }
        with pytest.raises(ValidationError):
            DishCreate(**data)


class TestOrderSchemas:
    def test_order_create_valid(self):
        """Тест создания заказа с валидными данными."""
        data = {
            "restaurant_id": 1,
            "delivery_address": "Test Address",
            "payment_method": PaymentMethod.CARD,
            "items": [{"dish_id": 1, "quantity": 2}, {"dish_id": 2, "quantity": 1}],
        }
        order = OrderCreate(**data)
        assert order.restaurant_id == 1
        assert len(order.items) == 2
        assert order.items[0].quantity == 2

    def test_order_create_no_items(self):
        """Тест создания заказа без блюд."""
        data = {
            "restaurant_id": 1,
            "delivery_address": "Test Address",
            "payment_method": PaymentMethod.CARD,
            "items": [],
        }
        with pytest.raises(ValidationError):
            OrderCreate(**data)

    def test_order_item_quantity_zero(self):
        """Тест с нулевым количеством блюд."""
        data = {"dish_id": 1, "quantity": 0}  # меньше минимального (1)
        with pytest.raises(ValidationError):
            OrderItemCreate(**data)

    def test_order_item_quantity_too_high(self):
        """Тест со слишком большим количеством."""
        data = {"dish_id": 1, "quantity": 200}  # больше максимального (100)
        with pytest.raises(ValidationError):
            OrderItemCreate(**data)


class TestFavoriteSchemas:
    def test_favorite_create_restaurant(self):
        """Тест добавления ресторана в избранное."""
        data = {"restaurant_id": 1}
        favorite = FavoriteCreate(**data)
        assert favorite.restaurant_id == 1
        assert favorite.dish_id is None

    def test_favorite_create_dish(self):
        """Тест добавления блюда в избранное."""
        data = {"dish_id": 1}
        favorite = FavoriteCreate(**data)
        assert favorite.dish_id == 1
        assert favorite.restaurant_id is None

    def test_favorite_create_both(self):
        """Тест добавления и ресторана, и блюда одновременно."""
        data = {"restaurant_id": 1, "dish_id": 1}
        with pytest.raises(ValidationError):
            FavoriteCreate(**data)

    def test_favorite_create_none(self):
        """Тест без указания ни ресторана, ни блюда."""
        data = {}
        with pytest.raises(ValidationError):
            FavoriteCreate(**data)


class TestReviewSchemas:
    def test_review_create_valid(self):
        """Тест создания отзыва с валидными данными."""
        data = {"restaurant_id": 1, "rating": 4.5, "comment": "Great food!"}
        review = ReviewCreate(**data)
        assert review.rating == 4.5
        assert review.restaurant_id == 1

    def test_review_create_rating_too_low(self):
        """Тест с рейтингом меньше 1."""
        data = {"restaurant_id": 1, "rating": 0.5}
        with pytest.raises(ValidationError):
            ReviewCreate(**data)

    def test_review_create_rating_too_high(self):
        """Тест с рейтингом больше 5."""
        data = {"restaurant_id": 1, "rating": 5.5}
        with pytest.raises(ValidationError):
            ReviewCreate(**data)

    def test_review_create_no_target(self):
        """Тест без указания ресторана или блюда."""
        data = {"rating": 4.0}
        with pytest.raises(ValidationError):
            ReviewCreate(**data)


# Тесты граничных значений
class TestBoundaryValues:
    def test_string_length_boundaries(self):
        """Тест граничных значений длины строк."""
        # Минимальная длина username
        data = {
            "email": "test@example.com",
            "username": "abc",  # минимальная длина 3
            "password": "Password123",
        }
        user = UserCreate(**data)
        assert user.username == "abc"

        # Слишком короткий username
        data["username"] = "ab"  # длина 2
        with pytest.raises(ValidationError):
            UserCreate(**data)

    def test_numeric_boundaries(self):
        """Тест граничных значений числовых полей."""
        # Минимальное время доставки
        data = {
            "name": "Test",
            "address": "Address",
            "delivery_time_min": 5,  # минимальное значение
        }
        restaurant = RestaurantCreate(**data)
        assert restaurant.delivery_time_min == 5

        # Ниже минимального
        data["delivery_time_min"] = 4
        with pytest.raises(ValidationError):
            RestaurantCreate(**data)

        # Максимальное время доставки
        data["delivery_time_min"] = 180  # максимальное значение
        restaurant = RestaurantCreate(**data)
        assert restaurant.delivery_time_min == 180

        # Выше максимального
        data["delivery_time_min"] = 181
        with pytest.raises(ValidationError):
            RestaurantCreate(**data)

    def test_price_boundaries(self):
        """Тест граничных значений цены."""
        # Минимальная цена (больше 0)
        data = {"restaurant_id": 1, "name": "Test Dish", "price": 0.01}  # чуть больше 0
        dish = DishCreate(**data)
        assert dish.price == 0.01

        # Цена равна 0
        data["price"] = 0.0
        with pytest.raises(ValidationError):
            DishCreate(**data)

        # Максимальная цена
        data["price"] = 10000.0  # максимальное значение
        dish = DishCreate(**data)
        assert dish.price == 10000.0

        # Выше максимального
        data["price"] = 10000.01
        with pytest.raises(ValidationError):
            DishCreate(**data)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
