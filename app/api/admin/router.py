from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import require_admin
from app.models.dish import Dish
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.dish import DishResponse, DishUpdate
from app.schemas.order import OrderResponse, OrderUpdate
from app.schemas.restaurant import RestaurantResponse, RestaurantUpdate
from app.schemas.user import UserResponse, UserUpdate

router = APIRouter(prefix="/admin", tags=["Admin"])


# Статистика
@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    """
    Получить статистику для админ-панели.
    """
    total_users = db.query(User).count()
    total_restaurants = db.query(Restaurant).count()
    total_dishes = db.query(Dish).count()
    total_orders = db.query(Order).count()

    active_orders = (
        db.query(Order)
        .filter(
            Order.status.in_(
                ["pending", "confirmed", "preparing", "ready", "on_delivery"]
            )
        )
        .count()
    )

    today_orders = (
        db.query(Order)
        .filter(db.func.date(Order.created_at) == db.func.current_date())
        .count()
    )

    return {
        "total_users": total_users,
        "total_restaurants": total_restaurants,
        "total_dishes": total_dishes,
        "total_orders": total_orders,
        "active_orders": active_orders,
        "today_orders": today_orders,
        "revenue_today": 0.0,  # Здесь можно добавить реальную логику
        "revenue_month": 0.0,
    }


# Управление пользователями
@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Получить список всех пользователей (админ).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.patch("/users/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Активировать пользователя.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_active = True
    db.commit()
    return {"message": "Пользователь активирован"}


@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Деактивировать пользователя.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.is_active = False
    db.commit()
    return {"message": "Пользователь деактивирован"}


@router.patch("/users/{user_id}/role")
def change_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Изменить роль пользователя.
    """
    from app.models.user import UserRole

    if new_role not in [role.value for role in UserRole]:
        raise HTTPException(status_code=400, detail="Недопустимая роль")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    user.role = UserRole(new_role)
    db.commit()
    return {"message": f"Роль пользователя изменена на {new_role}"}


# Управление заказами (админские функции)
@router.get("/orders/recent", response_model=List[OrderResponse])
def get_recent_orders(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Получить последние заказы.
    """
    orders = db.query(Order).order_by(Order.created_at.desc()).limit(limit).all()
    return orders


@router.post("/restaurants/{restaurant_id}/dishes/import")
def import_dishes_from_csv(
    restaurant_id: int,
    # Здесь будет загрузка файла
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Импорт блюд из CSV файла.
    """
    # Заглушка для импорта
    return {"message": "Импорт блюд (заглушка)"}


# Системные функции
@router.post("/system/clear-cache")
def clear_cache(current_user: User = Depends(require_admin)):
    """
    Очистить кэш системы.
    """
    # Заглушка
    return {"message": "Кэш очищен"}


@router.get("/system/health")
def system_health(
    db: Session = Depends(get_db), current_user: User = Depends(require_admin)
):
    """
    Проверка здоровья системы.
    """
    # Проверка подключения к БД
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "database": db_status,
        "api": "healthy",
        "timestamp": "2023-01-01T00:00:00Z",
    }
