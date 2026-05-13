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


class DishCategory(str, enum.Enum):
    APPETIZER = "appetizer"
    MAIN = "main"
    DESSERT = "dessert"
    DRINK = "drink"
    SIDE = "side"


class Dish(Base):
    __tablename__ = "dishes"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(Enum(DishCategory), default=DishCategory.MAIN, nullable=False)
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    calories = Column(Integer, nullable=True)
    cooking_time_min = Column(Integer, default=15)  # минут
    rating = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    restaurant = relationship("Restaurant", back_populates="dishes")
    order_items = relationship("OrderItem", back_populates="dish")
    favorites = relationship("Favorite", back_populates="dish")
    reviews = relationship("Review", back_populates="dish")

    def __repr__(self):
        return f"<Dish(id={self.id}, name={self.name}, price={self.price})>"
