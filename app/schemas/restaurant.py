from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RestaurantBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    address: str = Field(..., max_length=200)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    email: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = None
    cover_url: Optional[str] = None
    delivery_time_min: int = Field(10, ge=5, le=180)
    delivery_fee: float = Field(0.0, ge=0.0, le=1000.0)
    min_order_amount: float = Field(0.0, ge=0.0, le=10000.0)


class RestaurantCreate(RestaurantBase):
    pass


class RestaurantUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    address: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, pattern=r"^\+?[1-9]\d{1,14}$")
    email: Optional[str] = Field(None, max_length=100)
    logo_url: Optional[str] = None
    cover_url: Optional[str] = None
    delivery_time_min: Optional[int] = Field(None, ge=5, le=180)
    delivery_fee: Optional[float] = Field(None, ge=0.0, le=1000.0)
    min_order_amount: Optional[float] = Field(None, ge=0.0, le=10000.0)
    is_active: Optional[bool] = None


class RestaurantInDB(RestaurantBase):
    id: int
    rating: float = Field(0.0, ge=0.0, le=5.0)
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)


class RestaurantResponse(RestaurantInDB):
    pass


class RestaurantList(BaseModel):
    items: list[RestaurantResponse]
    total: int
    page: int
    size: int
