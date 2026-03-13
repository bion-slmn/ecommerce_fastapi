from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from app.database import get_db
from app.auth.dependencies import get_current_user
from app.models.cart_items import CartItem
from app.models.products import Product
from app.models.user import User

router = APIRouter(prefix="/cart", tags=["cart"])


class AddToCartSchema(BaseModel):
    product_id: int
    quantity: int = Field(default=1, ge=1)


class UpdateCartSchema(BaseModel):
    quantity: int = Field(ge=0)   # 0 = remove


def format_cart(cart_items):
    items = []
    cart_total = 0.0
    for item in cart_items:
        line_total = float(item.product.price) * item.quantity
        cart_total += line_total
        items.append({
            "id": item.id,
            "quantity": item.quantity,
            "line_total": round(line_total, 2),
            "product": {
                "id": item.product.id,
                "name": item.product.name,
                "description": item.product.description,
                "price": float(item.product.price),
                "stock": item.product.stock,
                "category": item.product.category,
                "in_stock": item.product.stock > 0,
                "created_at": item.product.created_at.isoformat()
            }
        })
    return items, round(cart_total, 2)


@router.post("")
def add_to_cart(
    body: AddToCartSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    product = db.query(Product).filter(Product.id == body.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock == 0:
        raise HTTPException(status_code=400, detail="Product is out of stock")

    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.product_id == body.product_id
    ).first()

    if cart_item:
        new_quantity = cart_item.quantity + body.quantity
        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Quantity exceeds available stock ({product.stock} available)"
            )
        cart_item.quantity = new_quantity
    else:
        if body.quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Quantity exceeds available stock ({product.stock} available)"
            )
        cart_item = CartItem(
            user_id=current_user.id,
            product_id=body.product_id,
            quantity=body.quantity
        )
        db.add(cart_item)

    db.commit()
    db.refresh(cart_item)
    return JSONResponse(status_code=200, content={
        "item": {
            "id": cart_item.id,
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity
        }
    })


@router.get("")
def get_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    items, cart_total = format_cart(cart_items)
    return JSONResponse(status_code=200, content={"items": items, "cart_total": cart_total})


@router.patch("/{item_id}")
def update_cart_item(
    item_id: int,
    body: UpdateCartSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()

    # 404 if not found or doesn't belong to user
    if not cart_item or cart_item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cart item not found")

    # quantity 0 = remove
    if body.quantity == 0:
        db.delete(cart_item)
        db.commit()
        return JSONResponse(status_code=200, content={"message": "Item removed from cart"})

    # check stock
    if body.quantity > cart_item.product.stock:
        raise HTTPException(
            status_code=400,
            detail=f"Quantity exceeds available stock ({cart_item.product.stock} available)"
        )

    cart_item.quantity = body.quantity
    db.commit()
    db.refresh(cart_item)
    return JSONResponse(status_code=200, content={
        "message": "Cart item updated",
        "item": {
            "id": cart_item.id,
            "product_id": cart_item.product_id,
            "quantity": cart_item.quantity,
            "line_total": round(float(cart_item.product.price) * cart_item.quantity, 2)
        }
    })


@router.delete("/{item_id}")
def delete_cart_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_item = db.query(CartItem).filter(CartItem.id == item_id).first()

    if not cart_item or cart_item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cart item not found")

    db.delete(cart_item)
    db.commit()
    return JSONResponse(status_code=200, content={"message": "Item removed from cart"})


@router.delete("")
def clear_cart(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()

    if not cart_items:
        raise HTTPException(status_code=400, detail="Cart is already empty")

    # build SMS summary before deleting
    item_lines = "\n".join(
        [f"- {item.product.name} x{item.quantity} @ ${float(item.product.price)}"
         for item in cart_items]
    )
    cart_total = sum(float(item.product.price) * item.quantity for item in cart_items)

    # clear cart
    db.query(CartItem).filter(CartItem.user_id == current_user.id).delete()
    db.commit()

    # send SMS if user has a mobile number
    

    return JSONResponse(status_code=200, content={"message": "Cart cleared successfully"})