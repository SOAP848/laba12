from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.restaurant import Restaurant
from app.schemas.restaurant import RestaurantCreate, RestaurantUpdate


class RestaurantService:
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Restaurant], int]:
        """
        Получить список ресторанов с пагинацией и фильтрацией.
        Возвращает кортеж (список ресторанов, общее количество).
        """
        query = db.query(Restaurant)

        if is_active is not None:
            query = query.filter(Restaurant.is_active == is_active)

        total = query.count()
        restaurants = query.offset(skip).limit(limit).all()
        return restaurants, total

    @staticmethod
    def get_by_id(db: Session, restaurant_id: int) -> Optional[Restaurant]:
        """Получить ресторан по ID."""
        return db.query(Restaurant).get(restaurant_id)

    @staticmethod
    def create(db: Session, restaurant_data: RestaurantCreate) -> Restaurant:
        """Создать новый ресторан."""
        restaurant = Restaurant(**restaurant_data.model_dump())
        db.add(restaurant)
        db.commit()
        db.refresh(restaurant)
        return restaurant

    @staticmethod
    def update(
        db: Session, restaurant: Restaurant, update_data: RestaurantUpdate
    ) -> Restaurant:
        """Обновить данные ресторана."""
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(restaurant, field, value)
        db.commit()
        db.refresh(restaurant)
        return restaurant

    @staticmethod
    def delete(db: Session, restaurant: Restaurant) -> None:
        """Удалить ресторан."""
        db.delete(restaurant)
        db.commit()

    @staticmethod
    def toggle_active(db: Session, restaurant: Restaurant, active: bool) -> Restaurant:
        """Активировать/деактивировать ресторан."""
        restaurant.is_active = active
        db.commit()
        db.refresh(restaurant)
        return restaurant