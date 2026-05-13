from sqlalchemy import (Boolean, Column, DateTime, Float, ForeignKey, Integer,
                        String, Text)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    cover_url = Column(String, nullable=True)
    rating = Column(Float, default=0.0)
    delivery_time_min = Column(Integer, default=30)  # минут
    delivery_fee = Column(Float, default=0.0)
    min_order_amount = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    dishes = relationship(
        "Dish", back_populates="restaurant", cascade="all, delete-orphan"
    )
    orders = relationship("Order", back_populates="restaurant")
    favorites = relationship("Favorite", back_populates="restaurant")
    reviews = relationship("Review", back_populates="restaurant")

    def __repr__(self):
        return f"<Restaurant(id={self.id}, name={self.name})>"
