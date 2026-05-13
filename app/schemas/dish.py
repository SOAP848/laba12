from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


class DishCategory(str, Enum):
    APPETIZER = "appetizer"
    MAIN = "main"
    DESSERT = "dessert"
    DRINK = "drink"
    SIDE = "side"


class DishBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0.0, le=10000.0)
    category: DishCategory = DishCategory.MAIN
    image_url: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0, le=10000)
    cooking_time_min: int = Field(5, ge=1, le=300)
    is_available: bool = True


class DishCreate(DishBase):
    restaurant_id: int


class DishUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0.0, le=10000.0)
    category: Optional[DishCategory] = None
    image_url: Optional[str] = None
    calories: Optional[int] = Field(None, ge=0, le=10000)
    cooking_time_min: Optional[int] = Field(None, ge=1, le=300)
    is_available: Optional[bool] = None


class DishInDB(DishBase):
    id: int
    restaurant_id: int
    rating: float = Field(0.0, ge=0.0, le=5.0)
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class DishResponse(DishInDB):
    pass


class DishList(BaseModel):
    items: list[DishResponse]
    total: int
    page: int
    size: int
