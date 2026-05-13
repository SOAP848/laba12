from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Enum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    ON_DELIVERY = "on_delivery"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    FAILED = "failed"


class PaymentMethod(str, enum.Enum):
    CASH = "cash"
    CARD = "card"
    ONLINE = "online"


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    total_amount = Column(Float, nullable=False)
    delivery_address = Column(String, nullable=False)
    delivery_notes = Column(Text, nullable=True)
    payment_method = Column(
        Enum(PaymentMethod), default=PaymentMethod.CASH, nullable=False
    )
    payment_status = Column(
        Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False
    )
    estimated_delivery_time = Column(DateTime(timezone=True), nullable=True)
    actual_delivery_time = Column(DateTime(timezone=True), nullable=True)
    courier_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="orders")
    restaurant = relationship("Restaurant", back_populates="orders")
    courier = relationship("User", foreign_keys=[courier_id])
    items = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )
    tracking = relationship(
        "OrderTracking", back_populates="order", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Order(id={self.id}, status={self.status}, total={self.total_amount})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)

    # Relationships
    order = relationship("Order", back_populates="items")
    dish = relationship("Dish", back_populates="order_items")

    def __repr__(self):
        return (
            f"<OrderItem(id={self.id}, dish={self.dish_id}, quantity={self.quantity})>"
        )
