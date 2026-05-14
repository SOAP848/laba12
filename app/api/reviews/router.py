from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.models.dish import Dish
from app.models.order import Order
from app.models.restaurant import Restaurant
from app.models.review import Review
from app.models.user import User, UserRole
from app.schemas.review import ReviewCreate, ReviewList, ReviewResponse, ReviewUpdate

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.get("/", response_model=ReviewList)
def list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    restaurant_id: Optional[int] = Query(None),
    dish_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    order_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить список отзывов с возможностью фильтрации.
    """
    query = db.query(Review)

    if restaurant_id is not None:
        query = query.filter(Review.restaurant_id == restaurant_id)
    if dish_id is not None:
        query = query.filter(Review.dish_id == dish_id)
    if user_id is not None:
        query = query.filter(Review.user_id == user_id)
    if order_id is not None:
        query = query.filter(Review.order_id == order_id)

    # Если не админ, показываем только свои отзывы или публичные?
    # Решаем: пользователь видит все отзывы (публичные), но можно ограничить.
    # Оставим как есть.

    total = query.count()
    reviews = query.offset(skip).limit(limit).all()

    return ReviewList(items=reviews, total=total, page=skip // limit + 1, size=limit)


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Создать новый отзыв.
    Требуется указать restaurant_id ИЛИ dish_id.
    Можно также указать order_id (опционально).
    """
    # Проверка, что указан ровно один целевой объект (валидатор схемы уже это делает)
    # Дополнительная проверка существования ресторана/блюда/заказа
    if review_data.restaurant_id:
        restaurant = db.query(Restaurant).get(review_data.restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Ресторан не найден")
    if review_data.dish_id:
        dish = db.query(Dish).get(review_data.dish_id)
        if not dish:
            raise HTTPException(status_code=404, detail="Блюдо не найдено")
    if review_data.order_id:
        order = db.query(Order).get(review_data.order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        # Проверка, что заказ принадлежит текущему пользователю
        if order.user_id != current_user.id:
            raise HTTPException(
                status_code=403, detail="Нельзя оставить отзыв на чужой заказ"
            )

    # Проверка, не оставлял ли пользователь уже отзыв на этот объект
    existing = (
        db.query(Review)
        .filter(
            Review.user_id == current_user.id,
            Review.restaurant_id == review_data.restaurant_id,
            Review.dish_id == review_data.dish_id,
            Review.order_id == review_data.order_id,
        )
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="Вы уже оставили отзыв на этот объект"
        )

    review = Review(
        **review_data.model_dump(),
        user_id=current_user.id,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить отзыв по ID.
    """
    review = db.query(Review).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")
    return review


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Обновить отзыв (только автор или администратор).
    """
    review = db.query(Review).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")

    if review.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    for field, value in review_data.model_dump(exclude_unset=True).items():
        setattr(review, field, value)

    db.commit()
    db.refresh(review)
    return review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить отзыв (только автор или администратор).
    """
    review = db.query(Review).get(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Отзыв не найден")

    if review.user_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(status_code=403, detail="Недостаточно прав")

    db.delete(review)
    db.commit()
    return None
