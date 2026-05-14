from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import (
    get_current_user,
    require_admin,
    require_restaurant_manager,
)
from app.models.dish import Dish
from app.models.order import Order, OrderItem, OrderStatus, PaymentStatus
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderItemCreate,
    OrderList,
    OrderResponse,
    OrderUpdate,
)
from app.tasks.email_tasks import send_order_confirmation

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("/", response_model=OrderList)
def list_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    restaurant_id: Optional[int] = None,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить список заказов с фильтрацией.
    Пользователи видят только свои заказы, администраторы видят все.
    """
    query = db.query(Order)

    # Ограничение для обычных пользователей
    if current_user.role not in ["admin", "restaurant_manager"]:
        query = query.filter(Order.user_id == current_user.id)

    if status is not None:
        query = query.filter(Order.status == status)

    if restaurant_id is not None:
        query = query.filter(Order.restaurant_id == restaurant_id)

    if user_id is not None and current_user.role in ["admin", "restaurant_manager"]:
        query = query.filter(Order.user_id == user_id)

    total = query.count()
    orders = query.offset(skip).limit(limit).all()

    return OrderList(items=orders, total=total, page=skip // limit + 1, size=limit)


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить информацию о заказе по ID.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден"
        )

    # Проверка прав доступа
    if (
        current_user.role not in ["admin", "restaurant_manager"]
        and order.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Нет доступа к этому заказу"
        )

    return order


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать новый заказ.
    """
    # Проверка существования ресторана
    restaurant = (
        db.query(Restaurant).filter(Restaurant.id == order_data.restaurant_id).first()
    )
    if not restaurant or not restaurant.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ресторан не найден или неактивен",
        )

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
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Блюдо с ID {item.dish_id} недоступно или не принадлежит ресторану",
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Минимальная сумма заказа {restaurant.min_order_amount}",
        )

    # Создание заказа
    db_order = Order(
        user_id=current_user.id,
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

    # Отправка подтверждения заказа через Celery (асинхронно)
    send_order_confirmation.delay(order_id=db_order.id, customer_email=current_user.email)

    return db_order


@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_data: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Обновить заказ (только для администраторов).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден"
        )

    update_data = order_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)

    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Отменить заказ.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден"
        )

    # Проверка прав
    if (
        current_user.role not in ["admin", "restaurant_manager"]
        and order.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав для отмены этого заказа",
        )

    # Можно отменять только заказы в определенных статусах
    if order.status not in [
        OrderStatus.PENDING,
        OrderStatus.CONFIRMED,
        OrderStatus.PREPARING,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно отменить заказ в текущем статусе",
        )

    order.status = OrderStatus.CANCELLED
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    new_status: OrderStatus,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_restaurant_manager),
):
    """
    Обновить статус заказа (только для менеджеров ресторанов и администраторов).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден"
        )

    # Проверка, что ресторан принадлежит менеджеру (если менеджер)
    if current_user.role == "restaurant_manager":
        # Здесь можно добавить проверку связи менеджера с рестораном
        pass

    order.status = new_status
    db.commit()
    db.refresh(order)
    return order
