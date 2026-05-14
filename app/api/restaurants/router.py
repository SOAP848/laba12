from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.cache import cache
from app.core.database import get_db
from app.dependencies.auth import (
    get_current_user,
    require_admin,
    require_restaurant_manager,
)
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.restaurant import (
    RestaurantCreate,
    RestaurantList,
    RestaurantResponse,
    RestaurantUpdate,
)

router = APIRouter(prefix="/restaurants", tags=["Restaurants"])


@router.get("/", response_model=RestaurantList)
def list_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """
    Получить список ресторанов с пагинацией.
    """
    # Формируем ключ кэша на основе параметров
    cache_key = f"restaurants:list:{skip}:{limit}:{is_active}"
    cached = cache.get(cache_key)
    if cached is not None:
        return RestaurantList(**cached)

    query = db.query(Restaurant)

    if is_active is not None:
        query = query.filter(Restaurant.is_active == is_active)

    total = query.count()
    restaurants = query.offset(skip).limit(limit).all()

    result = RestaurantList(
        items=restaurants, total=total, page=skip // limit + 1, size=limit
    )
    # Кэшируем на 5 минут (300 секунд)
    cache.set(cache_key, result.dict(), expire=300)
    return result


@router.get("/{restaurant_id}", response_model=RestaurantResponse)
def get_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """
    Получить информацию о ресторане по ID.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ресторан не найден"
        )
    return restaurant


@router.post(
    "/", response_model=RestaurantResponse, status_code=status.HTTP_201_CREATED
)
def create_restaurant(
    restaurant_data: RestaurantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Создать новый ресторан (только для администраторов).
    """
    # Проверка уникальности имени
    existing = (
        db.query(Restaurant).filter(Restaurant.name == restaurant_data.name).first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ресторан с таким названием уже существует",
        )

    db_restaurant = Restaurant(**restaurant_data.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    # Инвалидация кэша списков ресторанов
    cache.clear_pattern("restaurants:list:*")
    return db_restaurant


@router.put("/{restaurant_id}", response_model=RestaurantResponse)
def update_restaurant(
    restaurant_id: int,
    restaurant_data: RestaurantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Обновить информацию о ресторане (только для администраторов).
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ресторан не найден"
        )

    update_data = restaurant_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(restaurant, field, value)

    db.commit()
    db.refresh(restaurant)
    # Инвалидация кэша списков ресторанов
    cache.clear_pattern("restaurants:list:*")
    return restaurant


@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Удалить ресторан (только для администраторов).
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ресторан не найден"
        )

    db.delete(restaurant)
    db.commit()
    # Инвалидация кэша списков ресторанов
    cache.clear_pattern("restaurants:list:*")
    return None


@router.patch("/{restaurant_id}/activate", response_model=RestaurantResponse)
def activate_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Активировать ресторан.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ресторан не найден"
        )

    restaurant.is_active = True
    db.commit()
    db.refresh(restaurant)
    # Инвалидация кэша списков ресторанов
    cache.clear_pattern("restaurants:list:*")
    return restaurant


@router.patch("/{restaurant_id}/deactivate", response_model=RestaurantResponse)
def deactivate_restaurant(
    restaurant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """
    Деактивировать ресторан.
    """
    restaurant = db.query(Restaurant).filter(Restaurant.id == restaurant_id).first()
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ресторан не найден"
        )

    restaurant.is_active = False
    db.commit()
    db.refresh(restaurant)
    # Инвалидация кэша списков ресторанов
    cache.clear_pattern("restaurants:list:*")
    return restaurant
