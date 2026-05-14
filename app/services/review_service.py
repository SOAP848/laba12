from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewUpdate


class ReviewService:
    @staticmethod
    def get_all(
        db: Session,
        skip: int = 0,
        limit: int = 20,
        restaurant_id: Optional[int] = None,
        dish_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> tuple[List[Review], int]:
        """
        Получить список отзывов с фильтрацией.
        Возвращает кортеж (список отзывов, общее количество).
        """
        query = db.query(Review)

        if restaurant_id is not None:
            query = query.filter(Review.restaurant_id == restaurant_id)

        if dish_id is not None:
            query = query.filter(Review.dish_id == dish_id)

        if user_id is not None:
            query = query.filter(Review.user_id == user_id)

        total = query.count()
        reviews = query.offset(skip).limit(limit).all()
        return reviews, total

    @staticmethod
    def get_by_id(db: Session, review_id: int) -> Optional[Review]:
        """Получить отзыв по ID."""
        return db.query(Review).get(review_id)

    @staticmethod
    def create(db: Session, review_data: ReviewCreate, user: User) -> Review:
        """Создать новый отзыв."""
        # Проверка, что указан ровно один целевой объект
        if not (review_data.restaurant_id is None) ^ (review_data.dish_id is None):
            raise ValueError("Должен быть указан ровно один целевой объект (ресторан или блюдо)")

        # Проверка, что пользователь ещё не оставлял отзыв на этот объект
        existing = (
            db.query(Review)
            .filter(
                Review.user_id == user.id,
                Review.restaurant_id == review_data.restaurant_id,
                Review.dish_id == review_data.dish_id,
            )
            .first()
        )
        if existing:
            raise ValueError("Вы уже оставляли отзыв на этот объект")

        review = Review(**review_data.model_dump(), user_id=user.id)
        db.add(review)
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def update(
        db: Session, review: Review, update_data: ReviewUpdate
    ) -> Review:
        """Обновить данные отзыва."""
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(review, field, value)
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def delete(db: Session, review: Review) -> None:
        """Удалить отзыв."""
        db.delete(review)
        db.commit()

    @staticmethod
    def get_average_rating(
        db: Session,
        restaurant_id: Optional[int] = None,
        dish_id: Optional[int] = None,
    ) -> Optional[float]:
        """Получить средний рейтинг для ресторана или блюда."""
        query = db.query(Review)

        if restaurant_id is not None:
            query = query.filter(Review.restaurant_id == restaurant_id)
        elif dish_id is not None:
            query = query.filter(Review.dish_id == dish_id)
        else:
            return None

        ratings = query.with_entities(Review.rating).all()
        if not ratings:
            return None

        total = sum(r[0] for r in ratings)
        return total / len(ratings)

    @staticmethod
    def get_user_reviews(db: Session, user_id: int, skip: int = 0, limit: int = 20) -> tuple[List[Review], int]:
        """Получить отзывы конкретного пользователя."""
        query = db.query(Review).filter(Review.user_id == user_id)
        total = query.count()
        reviews = query.offset(skip).limit(limit).all()
        return reviews, total

    @staticmethod
    def get_restaurant_reviews(db: Session, restaurant_id: int, skip: int = 0, limit: int = 20) -> tuple[List[Review], int]:
        """Получить отзывы конкретного ресторана."""
        query = db.query(Review).filter(Review.restaurant_id == restaurant_id)
        total = query.count()
        reviews = query.offset(skip).limit(limit).all()
        return reviews, total

    @staticmethod
    def get_dish_reviews(db: Session, dish_id: int, skip: int = 0, limit: int = 20) -> tuple[List[Review], int]:
        """Получить отзывы конкретного блюда."""
        query = db.query(Review).filter(Review.dish_id == dish_id)
        total = query.count()
        reviews = query.offset(skip).limit(limit).all()
        return reviews, total