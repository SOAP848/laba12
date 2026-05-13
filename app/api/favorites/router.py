from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.dish import Dish
from app.models.favorite import Favorite
from app.models.restaurant import Restaurant
from app.models.user import User
from app.schemas.favorite import FavoriteCreate, FavoriteList, FavoriteResponse

router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("/", response_model=FavoriteList)
def list_favorites(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    type: Optional[str] = Query(None, description="Тип: 'restaurant' или 'dish'"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Получить список избранного текущего пользователя.
    """
    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)

    if type == "restaurant":
        query = query.filter(Favorite.restaurant_id.isnot(None))
    elif type == "dish":
        query = query.filter(Favorite.dish_id.isnot(None))

    total = query.count()
    favorites = query.offset(skip).limit(limit).all()

    return FavoriteList(
        items=favorites, total=total, page=skip // limit + 1, size=limit
    )


@router.post("/", response_model=FavoriteResponse, status_code=status.HTTP_201_CREATED)
def add_to_favorites(
    favorite_data: FavoriteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Добавить ресторан или блюдо в избранное.
    """
    # Проверка существования ресторана или блюда
    if favorite_data.restaurant_id:
        restaurant = (
            db.query(Restaurant)
            .filter(
                Restaurant.id == favorite_data.restaurant_id,
                Restaurant.is_active == True,
            )
            .first()
        )
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ресторан не найден или неактивен",
            )

        # Проверка, уже ли в избранном
        existing = (
            db.query(Favorite)
            .filter(
                Favorite.user_id == current_user.id,
                Favorite.restaurant_id == favorite_data.restaurant_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ресторан уже в избранном",
            )

    if favorite_data.dish_id:
        dish = (
            db.query(Dish)
            .filter(Dish.id == favorite_data.dish_id, Dish.is_available == True)
            .first()
        )
        if not dish:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Блюдо не найдено или недоступно",
            )

        existing = (
            db.query(Favorite)
            .filter(
                Favorite.user_id == current_user.id,
                Favorite.dish_id == favorite_data.dish_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Блюдо уже в избранном"
            )

    db_favorite = Favorite(user_id=current_user.id, **favorite_data.dict())

    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


@router.delete("/{favorite_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_favorites(
    favorite_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить из избранного по ID записи.
    """
    favorite = (
        db.query(Favorite)
        .filter(Favorite.id == favorite_id, Favorite.user_id == current_user.id)
        .first()
    )

    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись в избранном не найдена",
        )

    db.delete(favorite)
    db.commit()
    return None


@router.delete("/by-target", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_favorites_by_target(
    restaurant_id: Optional[int] = None,
    dish_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Удалить из избранного по ID ресторана или блюда.
    """
    if not restaurant_id and not dish_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите restaurant_id или dish_id",
        )

    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)

    if restaurant_id:
        query = query.filter(Favorite.restaurant_id == restaurant_id)
    if dish_id:
        query = query.filter(Favorite.dish_id == dish_id)

    favorite = query.first()
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Запись в избранном не найдена",
        )

    db.delete(favorite)
    db.commit()
    return None


@router.get("/check")
def check_favorite(
    restaurant_id: Optional[int] = None,
    dish_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Проверить, находится ли ресторан или блюдо в избранном.
    """
    if not restaurant_id and not dish_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Укажите restaurant_id или dish_id",
        )

    query = db.query(Favorite).filter(Favorite.user_id == current_user.id)

    if restaurant_id:
        query = query.filter(Favorite.restaurant_id == restaurant_id)
    if dish_id:
        query = query.filter(Favorite.dish_id == dish_id)

    favorite = query.first()
    return {"is_favorite": favorite is not None}
