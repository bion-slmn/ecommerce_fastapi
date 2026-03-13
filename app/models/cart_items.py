from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import declarative_base, relationship
from database import Base


class CartItem(Base):
    __tablename__ = 'cart_item'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Optional: relationships for easier joins
    user = relationship("User", backref="cart_items")
    product = relationship("Product", backref="cart_items")