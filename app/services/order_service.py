from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.dish import Dish
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.order import OrderCreate, OrderItemCreate, OrderUpdate


class OrderService:
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        status: Optional[OrderStatus] = None,
        restaurant_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> tuple[List[Order], int]:
        """
        Получить список заказов с фильтрацией.
        Возвращает кортеж (список заказов, общее количество).
        """
        query = db.query(Order)

        if status is not None:
            query = query.filter(Order.status == status)

        if restaurant_id is not None:
            query = query.filter(Order.restaurant_id == restaurant_id)

        if user_id is not None:
            query = query.filter(Order.user_id == user_id)

        total = query.count()
        orders = query.offset(skip).limit(limit).all()
        return orders, total

    @staticmethod
    def get_by_id(db: Session, order_id: int) -> Optional[Order]:
        """Получить заказ по ID."""
        return db.query(Order).get(order_id)

    @staticmethod
    def create(db: Session, order_data: OrderCreate, user: User) -> Order:
        """Создать новый заказ."""
        # Проверка существования ресторана
        restaurant = (
            db.query(Restaurant)
            .filter(Restaurant.id == order_data.restaurant_id)
            .first()
        )
        if not restaurant or not restaurant.is_active:
            raise ValueError("Ресторан не найден или неактивен")

        total_amount = 0.0
        order_items = []

        # Проверка каждого блюда
        for item in order_data.items:
            dish = (
                db.query(Dish)
                .filter(
                    Dish.id == item.dish_id,
                    Dish.restaurant_id == order_data.restaurant_id,
                    Dish.is_available == True,
                )
                .first()
            )

            if not dish:
                raise ValueError(
                    f"Блюдо с ID {item.dish_id} недоступно или не принадлежит ресторану"
                )

            total_amount += dish.price * item.quantity

            order_items.append(
                OrderItem(
                    dish_id=item.dish_id,
                    quantity=item.quantity,
                    unit_price=dish.price,
                    notes=item.notes,
                )
            )

        # Проверка минимальной суммы заказа
        if total_amount < restaurant.min_order_amount:
            raise ValueError(f"Минимальная сумма заказа {restaurant.min_order_amount}")

        # Создание заказа
        db_order = Order(
            user_id=user.id,
            restaurant_id=order_data.restaurant_id,
            status=OrderStatus.PENDING,
            total_amount=total_amount + restaurant.delivery_fee,
            delivery_address=order_data.delivery_address,
            delivery_notes=order_data.delivery_notes,
            payment_method=order_data.payment_method,
            payment_status=PaymentStatus.PENDING,
            items=order_items,
        )

        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order

    @staticmethod
    def update(db: Session, order: Order, update_data: OrderUpdate) -> Order:
        """Обновить данные заказа."""
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(order, field, value)
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def delete(db: Session, order: Order) -> None:
        """Удалить заказ."""
        db.delete(order)
        db.commit()

    @staticmethod
    def update_status(db: Session, order: Order, new_status: OrderStatus) -> Order:
        """Обновить статус заказа."""
        order.status = new_status
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def cancel_order(db: Session, order: Order) -> Order:
        """Отменить заказ."""
        if order.status not in [
            OrderStatus.PENDING,
            OrderStatus.CONFIRMED,
            OrderStatus.PREPARING,
        ]:
            raise ValueError("Невозможно отменить заказ в текущем статусе")
        order.status = OrderStatus.CANCELLED
        db.commit()
        db.refresh(order)
        return order

    @staticmethod
    def get_user_orders(
        db: Session, user_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[Order], int]:
        """Получить заказы конкретного пользователя."""
        query = db.query(Order).filter(Order.user_id == user_id)
        total = query.count()
        orders = query.offset(skip).limit(limit).all()
        return orders, total

    @staticmethod
    def get_restaurant_orders(
        db: Session, restaurant_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[Order], int]:
        """Получить заказы конкретного ресторана."""
        query = db.query(Order).filter(Order.restaurant_id == restaurant_id)
        total = query.count()
        orders = query.offset(skip).limit(limit).all()
        return orders, total
