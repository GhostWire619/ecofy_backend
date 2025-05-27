from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from math import ceil

from app.api.deps import get_current_user
from app.database import get_db
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductCreate, ProductResponse, ProductBase

router = APIRouter()

@router.get("/products", response_model=dict)
def get_products(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    
    # Apply filters
    if category:
        query = query.filter(Product.category == category)
    
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    # Count total
    total = query.count()
    
    # Paginate
    query = query.offset((page - 1) * limit).limit(limit)
    
    # Get products
    products = query.all()
    
    # Get product items with seller names
    items = []
    for product in products:
        seller = db.query(User).filter(User.id == product.seller_id).first()
        seller_name = seller.full_name if seller else "Unknown"
        
        product_dict = {**product.__dict__}
        if "_sa_instance_state" in product_dict:
            del product_dict["_sa_instance_state"]
        
        product_dict["seller_name"] = seller_name
        items.append(product_dict)
    
    # Calculate total pages
    pages = ceil(total / limit) if total > 0 else 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "pages": pages
    }


@router.post("/products", response_model=ProductResponse)
def create_product(
    product_in: ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = Product(
        seller_id=current_user.id,
        name=product_in.name,
        description=product_in.description,
        price=product_in.price,
        quantity=product_in.quantity,
        unit=product_in.unit,
        category=product_in.category.value,
        location=product_in.location,
        images=product_in.images
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Get seller name
    seller = db.query(User).filter(User.id == current_user.id).first()
    
    return {
        **product.__dict__,
        "seller_name": seller.full_name
    }


@router.get("/products/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get seller name
    seller = db.query(User).filter(User.id == product.seller_id).first()
    seller_name = seller.full_name if seller else "Unknown"
    
    return {
        **product.__dict__,
        "seller_name": seller_name
    }


@router.put("/products/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: str,
    product_in: ProductBase,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.seller_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or you don't have permission to update it"
        )
    
    # Update product
    product.name = product_in.name
    product.description = product_in.description
    product.price = product_in.price
    product.quantity = product_in.quantity
    product.unit = product_in.unit
    product.category = product_in.category.value
    product.location = product_in.location
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Get seller name
    seller = db.query(User).filter(User.id == current_user.id).first()
    
    return {
        **product.__dict__,
        "seller_name": seller.full_name
    }


@router.delete("/products/{product_id}", response_model=dict)
def delete_product(
    product_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(
        Product.id == product_id,
        Product.seller_id == current_user.id
    ).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found or you don't have permission to delete it"
        )
    
    db.delete(product)
    db.commit()
    
    return {"success": True} 