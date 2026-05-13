from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_restaurant_manager
from app.models.user import User
from app.models.order import Order, OrderStatus
from app.models.tracking import OrderTracking
from app.schemas.order import OrderTrackingCreate, OrderTrackingResponse

router = APIRouter(prefix="/orders/{order_id}/tracking", tags=["Order Tracking"])


@router.get("/", response_model=List[OrderTrackingResponse])
def get_order_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить историю трекинга заказа.
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

    tracking = (
        db.query(OrderTracking)
        .filter(OrderTracking.order_id == order_id)
        .order_by(OrderTracking.created_at.desc())
        .all()
    )

    return tracking


@router.post(
    "/", response_model=OrderTrackingResponse, status_code=status.HTTP_201_CREATED
)
def add_tracking_event(
    order_id: int,
    tracking_data: OrderTrackingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_restaurant_manager),
):
    """
    Добавить событие трекинга заказа (только для менеджеров ресторанов и администраторов).
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Заказ не найден"
        )

    # Проверка, что заказ принадлежит ресторану менеджера (если нужно)
    # Здесь можно добавить дополнительную проверку

    db_tracking = OrderTracking(order_id=order_id, **tracking_data.dict())

    # Обновление статуса заказа, если статус указан в трекинге
    if tracking_data.status:
        # Маппинг статусов трекинга на статусы заказа
        status_map = {
            "preparing": OrderStatus.PREPARING,
            "ready": OrderStatus.READY,
            "on_the_way": OrderStatus.ON_DELIVERY,
            "delivered": OrderStatus.DELIVERED,
        }
        if tracking_data.status in status_map:
            order.status = status_map[tracking_data.status]

    db.add(db_tracking)
    db.commit()
    db.refresh(db_tracking)

    return db_tracking


@router.get("/current", response_model=OrderTrackingResponse)
def get_current_tracking(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить текущее состояние трекинга заказа.
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

    tracking = (
        db.query(OrderTracking)
        .filter(OrderTracking.order_id == order_id)
        .order_by(OrderTracking.created_at.desc())
        .first()
    )

    if not tracking:
        # Возвращаем базовую информацию из заказа
        return OrderTrackingResponse(
            id=0,
            order_id=order_id,
            status=order.status.value,
            description=f"Заказ создан. Статус: {order.status.value}",
            created_at=order.created_at,
        )

    return tracking


@router.get("/estimated-delivery")
def get_estimated_delivery(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить расчетное время доставки.
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

    # Логика расчета времени доставки
    # В реальном приложении здесь может быть сложная логика

    from datetime import datetime, timedelta
    import random

    if order.estimated_delivery_time:
        estimated = order.estimated_delivery_time
    else:
        # Примерная логика
        base_time = order.created_at
        estimated = base_time + timedelta(minutes=random.randint(30, 90))

    tracking = (
        db.query(OrderTracking)
        .filter(OrderTracking.order_id == order_id)
        .order_by(OrderTracking.created_at.desc())
        .first()
    )

    return {
        "order_id": order_id,
        "estimated_delivery_time": estimated,
        "current_status": order.status.value,
        "last_update": tracking.created_at if tracking else order.created_at,
        "remaining_minutes": max(
            0, int((estimated - datetime.utcnow()).total_seconds() / 60)
        ),
    }
