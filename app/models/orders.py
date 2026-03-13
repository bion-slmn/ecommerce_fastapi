from sqlalchemy import Column, Integer, Numeric, String, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

from app.database import Base
class Order(Base):
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(50), nullable=False, server_default='pending')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Optional relationship
    user = relationship("User", backref="orders")