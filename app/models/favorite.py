from sqlalchemy import Column, DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="favorites")
    restaurant = relationship("Restaurant", back_populates="favorites")
    dish = relationship("Dish", back_populates="favorites")

    # Ограничение: либо ресторан, либо блюдо, но не оба одновременно
    __table_args__ = (
        UniqueConstraint("user_id", "restaurant_id", name="unique_user_restaurant"),
        UniqueConstraint("user_id", "dish_id", name="unique_user_dish"),
    )

    def __repr__(self):
        return f"<Favorite(id={self.id}, user={self.user_id}, restaurant={self.restaurant_id}, dish={self.dish_id})>"
