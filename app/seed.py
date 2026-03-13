# seed_products.py
from sqlalchemy.orm import Session
from database import engine, Base

# Import models so Base knows about them
from models.products import Product
from models.user import User
from models.cart_items import CartItem
from models.orders import Order
from models.order_items import OrderItem

Base.metadata.create_all(bind=engine)

session = Session(bind=engine)

categories = ["Electronics", "Books", "Clothing"]

products = [
    {"name": "Laptop", "description": "A powerful laptop", "price": 1200.00, "stock": 10, "category": "Electronics"},
    {"name": "Smartphone", "description": "Latest smartphone", "price": 900.00, "stock": 0, "category": "Electronics"},
    {"name": "Headphones", "description": "Noise cancelling", "price": 200.00, "stock": 5, "category": "Electronics"},
    {"name": "Keyboard", "description": "Mechanical keyboard", "price": 150.00, "stock": 0, "category": "Electronics"},
    {"name": "Monitor", "description": "4K monitor", "price": 350.00, "stock": 7, "category": "Electronics"},
    {"name": "Book A", "description": "Fiction book", "price": 25.00, "stock": 20, "category": "Books"},
    {"name": "Book B", "description": "Non-fiction book", "price": 30.00, "stock": 15, "category": "Books"},
    {"name": "T-Shirt", "description": "Cotton t-shirt", "price": 20.00, "stock": 50, "category": "Clothing"},
    {"name": "Jeans", "description": "Denim jeans", "price": 40.00, "stock": 30, "category": "Clothing"},
    {"name": "Jacket", "description": "Winter jacket", "price": 100.00, "stock": 10, "category": "Clothing"},
]

for p in products:
    product = Product(
        name=p["name"],
        description=p["description"],
        price=p["price"],
        stock=p["stock"],
        category=p["category"]
    )
    session.add(product)

session.commit()
session.close()
print("Seeded 10 products across 3 categories successfully!")