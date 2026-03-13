from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.orders import Order
from app.models.user import User
from app.routers.order_service import (
    get_cart_items,
    validate_stock,
    check_duplicate_order,
    create_order
)

router = APIRouter(prefix="/orders", tags=["orders"])


def format_order(order: Order) -> dict:
    return {
        "id": order.id,
        "status": order.status,
        "total_amount": float(order.total_amount),
        "created_at": order.created_at.isoformat(),
        "items": [
            {
                "id": item.id,
                "product_id": item.product_id,
                "product_name": item.product.name,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "line_total": round(float(item.unit_price) * item.quantity, 2)
            }
            for item in order.items
        ]
    }


@router.post("/checkout", status_code=201)
def checkout(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # ✅ check duplicate FIRST — cart may already be cleared
        duplicate = check_duplicate_order(db, current_user.id)
        if duplicate:
            return JSONResponse(status_code=201, content={
                "message": "Returning recent order",
                "order": format_order(duplicate)
            })

        # only reach here if no duplicate
        cart_items = get_cart_items(db, current_user.id)

        locked_products = validate_stock(db, cart_items)
        order, order_items_summary = create_order(db, current_user.id, cart_items, locked_products)

        db.commit()
        db.refresh(order)

    

        return JSONResponse(status_code=202, content={
            "message": "Order placed successfully",
            "order": format_order(order)
        })

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Checkout failed: {str(e)}")


@router.get("")
def get_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    orders = (
        db.query(Order)
        .filter(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return JSONResponse(status_code=200, content={
        "orders": [format_order(order) for order in orders]
    })


@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order or order.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Order not found")
    return JSONResponse(status_code=200, content={"order": format_order(order)})