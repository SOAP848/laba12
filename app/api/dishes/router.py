from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.dependencies.auth import (
    require_admin,
    require_restaurant_manager,
    get_current_user,
)
from app.models.user import User
from app.models.restaurant import Restaurant
from app.models.dish import Dish
from app.schemas.dish import DishCreate, DishUpdate, DishResponse, DishList

router = APIRouter(prefix="/dishes", tags=["Dishes"])


@router.get("/", response_model=DishList)
def list_dishes(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    restaurant_id: Optional[int] = None,
    category: Optional[str] = None,
    is_available: Optional[bool] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    """
    Получить список блюд с фильтрацией.
    """
    query = db.query(Dish)

    if restaurant_id is not None:
        query = query.filter(Dish.restaurant_id == restaurant_id)

    if category is not None:
        query = query.filter(Dish.category == category)

    if is_available is not None:
        query = query.filter(Dish.is_available == is_available)

    if min_price is not None:
        query = query.filter(Dish.price >= min_price)

    if max_price is not None:
        query = query.filter(Dish.price <= max_price)

    total = query.count()
    dishes = query.offset(skip).limit(limit).all()

    return DishList(items=dishes, total=total, page=skip // limit + 1, size=limit)


@router.get("/{dish_id}", response_model=DishResponse)
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    """
    Получить информацию о блюде по ID.
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Блюдо не найдено"
        )
    return dish


@router.post("/", response_model=DishResponse, status_code=status.HTTP_201_CREATED)
def create_dish(
    dish_data: DishCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_restaurant_manager),
):
    """
    Создать новое блюдо (только для менеджеров ресторанов и администраторов).
    """
    # Проверка существования ресторана
    restaurant = (
        db.query(Restaurant).filter(Restaurant.id == dish_data.restaurant_id).first()
    )
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ресторан не найден"
        )

    # Проверка уникальности имени в рамках ресторана
    existing = (
        db.query(Dish)
        .filter(
            Dish.restaurant_id == dish_data.restaurant_id, Dish.name == dish_data.name
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Блюдо с таким названием уже существует в этом ресторане",
        )

    db_dish = Dish(**dish_data.dict())
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    return db_dish


@router.put("/{dish_id}", response_model=DishResponse)
def update_dish(
    dish_id: int,
    dish_data: DishUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_restaurant_manager),
):
    """
    Обновить информацию о блюде (только для менеджеров ресторанов и администраторов).
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Блюдо не найдено"
        )

    update_data = dish_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dish, field, value)

    db.commit()
    db.refresh(dish)
    return dish


@router.delete("/{dish_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_restaurant_manager),
):
    """
    Удалить блюдо (только для менеджеров ресторанов и администраторов).
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Блюдо не найдено"
        )

    db.delete(dish)
    db.commit()
    return None


@router.patch("/{dish_id}/activate", response_model=DishResponse)
def activate_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_restaurant_manager),
):
    """
    Активировать блюдо (сделать доступным).
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Блюдо не найдено"
        )

    dish.is_available = True
    db.commit()
    db.refresh(dish)
    return dish


@router.patch("/{dish_id}/deactivate", response_model=DishResponse)
def deactivate_dish(
    dish_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_restaurant_manager),
):
    """
    Деактивировать блюдо (сделать недоступным).
    """
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Блюдо не найдено"
        )

    dish.is_available = False
    db.commit()
    db.refresh(dish)
    return dish
