from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    ON_DELIVERY = "on_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"

class PaymentMethod(str, Enum):
    CASH = "cash"
    CARD = "card"
    ONLINE = "online"

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"

# Order Item
class OrderItemBase(BaseModel):
    dish_id: int
    quantity: int = Field(1, ge=1, le=100)
    notes: Optional[str] = Field(None, max_length=200)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItemResponse(OrderItemBase):
    id: int
    unit_price: float
    order_id: int

    model_config = ConfigDict(from_attributes=True)

# Order
class OrderBase(BaseModel):
    restaurant_id: int
    delivery_address: str = Field(..., max_length=200)
    delivery_notes: Optional[str] = Field(None, max_length=500)
    payment_method: PaymentMethod = PaymentMethod.CASH

class OrderCreate(OrderBase):
    items: list[OrderItemCreate] = Field(..., min_length=1)

    @field_validator('items')
    @classmethod
    def validate_items(cls, v: list[OrderItemCreate]) -> list[OrderItemCreate]:
        if not v:
            raise ValueError('Заказ должен содержать хотя бы одно блюдо')
        return v

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    delivery_address: Optional[str] = Field(None, max_length=200)
    delivery_notes: Optional[str] = Field(None, max_length=500)
    payment_method: Optional[PaymentMethod] = None
    payment_status: Optional[PaymentStatus] = None
    estimated_delivery_time: Optional[datetime] = None
    courier_id: Optional[int] = None

class OrderInDB(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float
    payment_status: PaymentStatus
    estimated_delivery_time: Optional[datetime]
    actual_delivery_time: Optional[datetime]
    courier_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)

class OrderResponse(OrderInDB):
    items: list[OrderItemResponse]

class OrderList(BaseModel):
    items: list[OrderResponse]
    total: int
    page: int
    size: int

# Tracking
class OrderTrackingBase(BaseModel):
    status: str = Field(..., max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    location_lat: Optional[str] = None
    location_lng: Optional[str] = None
    estimated_minutes: Optional[int] = Field(None, ge=0, le=300)

class OrderTrackingCreate(OrderTrackingBase):
    order_id: int

class OrderTrackingResponse(OrderTrackingBase):
    id: int
    order_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)