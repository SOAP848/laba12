from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.user import User
from app.schemas.favorite import FavoriteCreate


class FavoriteService:
    @staticmethod
    def get_all(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[List[Favorite], int]:
        """
        Получить список избранного пользователя.
        Возвращает кортеж (список избранного, общее количество).
        """
        query = db.query(Favorite).filter(Favorite.user_id == user_id)

        total = query.count()
        favorites = query.offset(skip).limit(limit).all()
        return favorites, total

    @staticmethod
    def get_by_id(db: Session, favorite_id: int) -> Optional[Favorite]:
        """Получить избранное по ID."""
        return db.query(Favorite).get(favorite_id)

    @staticmethod
    def create(db: Session, favorite_data: FavoriteCreate, user: User) -> Favorite:
        """Добавить в избранное."""
        # Проверка, что указан ровно один целевой объект
        if not (favorite_data.restaurant_id is None) ^ (favorite_data.dish_id is None):
            raise ValueError("Должен быть указан ровно один целевой объект (ресторан или блюдо)")

        # Проверка уникальности (чтобы не дублировать)
        existing = (
            db.query(Favorite)
            .filter(
                Favorite.user_id == user.id,
                Favorite.restaurant_id == favorite_data.restaurant_id,
                Favorite.dish_id == favorite_data.dish_id,
            )
            .first()
        )
        if existing:
            raise ValueError("Этот объект уже добавлен в избранное")

        favorite = Favorite(**favorite_data.model_dump(), user_id=user.id)
        db.add(favorite)
        db.commit()
        db.refresh(favorite)
        return favorite

    @staticmethod
    def delete(db: Session, favorite: Favorite) -> None:
        """Удалить из избранного."""
        db.delete(favorite)
        db.commit()

    @staticmethod
    def delete_by_target(
        db: Session,
        user_id: int,
        restaurant_id: Optional[int] = None,
        dish_id: Optional[int] = None,
    ) -> bool:
        """
        Удалить из избранного по целевым объектам.
        Возвращает True, если удаление выполнено.
        """
        query = db.query(Favorite).filter(Favorite.user_id == user_id)

        if restaurant_id is not None:
            query = query.filter(Favorite.restaurant_id == restaurant_id)
        if dish_id is not None:
            query = query.filter(Favorite.dish_id == dish_id)

        favorite = query.first()
        if not favorite:
            return False

        db.delete(favorite)
        db.commit()
        return True

    @staticmethod
    def check_favorite(
        db: Session,
        user_id: int,
        restaurant_id: Optional[int] = None,
        dish_id: Optional[int] = None,
    ) -> bool:
        """Проверить, добавлен ли объект в избранное."""
        query = db.query(Favorite).filter(Favorite.user_id == user_id)

        if restaurant_id is not None:
            query = query.filter(Favorite.restaurant_id == restaurant_id)
        if dish_id is not None:
            query = query.filter(Favorite.dish_id == dish_id)

        return query.first() is not None

    @staticmethod
    def get_user_favorites_count(db: Session, user_id: int) -> int:
        """Получить количество избранных объектов пользователя."""
        return db.query(Favorite).filter(Favorite.user_id == user_id).count()