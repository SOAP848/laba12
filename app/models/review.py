from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Float,
    DateTime,
    ForeignKey,
    CheckConstraint,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=True)
    dish_id = Column(Integer, ForeignKey("dishes.id"), nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    rating = Column(Float, nullable=False)  # от 1 до 5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="reviews")
    restaurant = relationship("Restaurant", back_populates="reviews")
    dish = relationship("Dish", back_populates="reviews")

    # Ограничение: рейтинг от 1 до 5
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range"),
    )

    def __repr__(self):
        return f"<Review(id={self.id}, rating={self.rating}, user={self.user_id})>"
