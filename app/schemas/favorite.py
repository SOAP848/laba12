from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from typing import Optional
from datetime import datetime


class FavoriteBase(BaseModel):
    restaurant_id: Optional[int] = None
    dish_id: Optional[int] = None

    @model_validator(mode="after")
    def validate_exactly_one(self):
        if self.restaurant_id is not None and self.dish_id is not None:
            raise ValueError(
                "Можно добавить в избранное либо ресторан, либо блюдо, но не оба одновременно"
            )
        if self.restaurant_id is None and self.dish_id is None:
            raise ValueError("Необходимо указать либо restaurant_id, либо dish_id")
        return self


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteUpdate(BaseModel):
    restaurant_id: Optional[int] = None
    dish_id: Optional[int] = None


class FavoriteInDB(FavoriteBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FavoriteResponse(FavoriteInDB):
    pass


class FavoriteList(BaseModel):
    items: list[FavoriteResponse]
    total: int
    page: int
    size: int
