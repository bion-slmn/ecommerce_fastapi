from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, func
from sqlalchemy.orm import declarative_base

from database import Base
class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    category = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)