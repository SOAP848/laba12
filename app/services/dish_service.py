from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.dish import Dish, DishCategory
from app.schemas.dish import DishCreate, DishUpdate


class DishService:
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        restaurant_id: Optional[int] = None,
        category: Optional[DishCategory] = None,
        is_available: Optional[bool] = None,
    ) -> tuple[List[Dish], int]:
        """
        Получить список блюд с фильтрацией.
        Возвращает кортеж (список блюд, общее количество).
        """
        query = db.query(Dish)

        if restaurant_id is not None:
            query = query.filter(Dish.restaurant_id == restaurant_id)

        if category is not None:
            query = query.filter(Dish.category == category)

        if is_available is not None:
            query = query.filter(Dish.is_available == is_available)

        total = query.count()
        dishes = query.offset(skip).limit(limit).all()
        return dishes, total

    @staticmethod
    def get_by_id(db: Session, dish_id: int) -> Optional[Dish]:
        """Получить блюдо по ID."""
        return db.query(Dish).get(dish_id)

    @staticmethod
    def create(db: Session, dish_data: DishCreate) -> Dish:
        """Создать новое блюдо."""
        dish = Dish(**dish_data.model_dump())
        db.add(dish)
        db.commit()
        db.refresh(dish)
        return dish

    @staticmethod
    def update(
        db: Session, dish: Dish, update_data: DishUpdate
    ) -> Dish:
        """Обновить данные блюда."""
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(dish, field, value)
        db.commit()
        db.refresh(dish)
        return dish

    @staticmethod
    def delete(db: Session, dish: Dish) -> None:
        """Удалить блюдо."""
        db.delete(dish)
        db.commit()

    @staticmethod
    def toggle_available(db: Session, dish: Dish, available: bool) -> Dish:
        """Изменить доступность блюда."""
        dish.is_available = available
        db.commit()
        db.refresh(dish)
        return dish

    @staticmethod
    def get_by_restaurant(
        db: Session, restaurant_id: int, skip: int = 0, limit: int = 20
    ) -> tuple[List[Dish], int]:
        """Получить блюда конкретного ресторана."""
        query = db.query(Dish).filter(Dish.restaurant_id == restaurant_id)
        total = query.count()
        dishes = query.offset(skip).limit(limit).all()
        return dishes, total