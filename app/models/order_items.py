

from sqlalchemy import Column, Integer, ForeignKey, Numeric
from sqlalchemy.orm import declarative_base, relationship

from database import Base

class OrderItem(Base):
    __tablename__ = 'order_items'

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(Integer, ForeignKey('product.id', ondelete='CASCADE'), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    # Optional relationships for easy access
    order = relationship("Order", backref="items")
    product = relationship("Product", backref="order_items")