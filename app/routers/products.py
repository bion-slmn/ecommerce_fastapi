from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.database import get_db
from app.models.products import Product
import math

router = APIRouter(prefix="/products", tags=["products"])


def format_product(p: Product) -> dict:
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "price": float(p.price),
        "stock": p.stock,
        "category": p.category,
        "in_stock": p.stock > 0,
        "created_at": p.created_at.isoformat()
    }


@router.get("")
def get_products(
    db: Session = Depends(get_db),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    category: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=50)
):
    query = db.query(Product)

  
    if category:
        query = query.filter(Product.category.ilike(f"%{category}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    total = query.count()
    total_pages = math.ceil(total / limit)
    products = query.offset((page - 1) * limit).limit(limit).all()

    return JSONResponse(status_code=200, content={
        "data": [format_product(p) for p in products],   # ✅ reuse helper
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages
        }
    })


@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return JSONResponse(status_code=200, content=format_product(product))