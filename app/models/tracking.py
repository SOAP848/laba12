from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class OrderTracking(Base):
    __tablename__ = "order_tracking"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    status = Column(String, nullable=False)  # например, "preparing", "on_the_way"
    description = Column(Text, nullable=True)
    location_lat = Column(String, nullable=True)
    location_lng = Column(String, nullable=True)
    estimated_minutes = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="tracking")

    def __repr__(self):
        return f"<OrderTracking(id={self.id}, order={self.order_id}, status={self.status})>"
