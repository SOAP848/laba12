from pydantic import BaseModel, Field, model_validator, ConfigDict
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    restaurant_id: Optional[int] = None
    dish_id: Optional[int] = None
    order_id: Optional[int] = None
    rating: float = Field(..., ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, max_length=1000)

    @model_validator(mode="after")
    def validate_at_least_one_target(self):
        if self.restaurant_id is None and self.dish_id is None:
            raise ValueError("Необходимо указать либо restaurant_id, либо dish_id")
        return self


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewInDB(ReviewBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class ReviewResponse(ReviewInDB):
    pass


class ReviewList(BaseModel):
    items: list[ReviewResponse]
    total: int
    page: int
    size: int
