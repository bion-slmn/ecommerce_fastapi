from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.cart_items import CartItem
from app.models.orders import Order
from app.models.order_items import OrderItem
from app.models.products import Product


def get_cart_items(db: Session, user_id: int) -> list:
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    return cart_items


def validate_stock(db: Session, cart_items: list) -> dict:
    """Lock products and collect ALL failures before raising."""
    failed_items = []
    locked_products = {}

    for item in cart_items:
        product = (
            db.query(Product)
            .filter(Product.id == item.product_id)
            .with_for_update()
            .first()
        )

        if not product:
            failed_items.append({
                "product_id": item.product_id,
                "reason": "Product no longer exists"
            })
            continue

        locked_products[item.product_id] = product

        if product.stock == 0:
            failed_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "reason": "Out of stock"
            })
        elif item.quantity > product.stock:
            failed_items.append({
                "product_id": product.id,
                "product_name": product.name,
                "requested": item.quantity,
                "available": product.stock,
                "reason": f"Only {product.stock} units available"
            })

    if failed_items:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Some products could not be fulfilled",
                "failed_items": failed_items
            }
        )

    return locked_products


def check_duplicate_order(db: Session, user_id: int) -> Order | None:
    """Return recent order placed within last 10 seconds."""
    ten_seconds_ago = datetime.now(timezone.utc) - timedelta(seconds=10)
    return (
        db.query(Order)
        .filter(
            Order.user_id == user_id,
            Order.created_at >= ten_seconds_ago
        )
        .order_by(Order.created_at.desc())
        .first()
    )

def create_order(db: Session, user_id: int, cart_items: list, locked_products: dict) -> tuple[Order, list]:
    """Create order, order items, deduct stock, clear cart."""
    total_amount = sum(
        float(locked_products[item.product_id].price) * item.quantity
        for item in cart_items
    )

    order = Order(
        user_id=user_id,
        total_amount=total_amount,
        status="pending"
    )
    db.add(order)
    db.flush()  # get order.id before commit

    order_items_summary = []
    for item in cart_items:
        product = locked_products[item.product_id]

        db.add(OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            unit_price=product.price    # ✅ snapshot at purchase time
        ))

        product.stock -= item.quantity

        order_items_summary.append({
            "product_id": product.id,
            "product_name": product.name,
            "quantity": item.quantity,
            "unit_price": float(product.price),
            "line_total": round(float(product.price) * item.quantity, 2)
        })

    # clear cart
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()

    return order, order_items_summary