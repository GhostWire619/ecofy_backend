from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user
from app.database import get_db
from app.models.order import Order
from app.models.product import Product
from app.models.user import User
from app.schemas.order import OrderCreate, OrderResponse, OrderStatus

router = APIRouter()

@router.post("", response_model=OrderResponse)
def create_order(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Calculate total amount
    total_amount = 0
    items = []
    
    for item in order_in.items:
        # Check if product exists and has enough quantity
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item.product_id} not found"
            )
        
        if product.quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Not enough quantity available for product {product.name}"
            )
        
        # Update product quantity
        product.quantity -= item.quantity
        db.add(product)
        
        # Add to total
        item_total = item.quantity * item.unit_price
        total_amount += item_total
        
        # Add item to list
        items.append(item.dict())
    
    # Create order
    order = Order(
        user_id=current_user.id,
        items=items,
        total_amount=total_amount,
        status=OrderStatus.PENDING.value,
        delivery_address=order_in.delivery_address,
        payment_method=order_in.payment_method
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order


@router.get("", response_model=List[OrderResponse])
def get_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Order).filter(Order.user_id == current_user.id).all()


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: str,
    status_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Get order
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update status
    new_status = status_data.get("status")
    if not new_status or new_status not in [e.value for e in OrderStatus]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join([e.value for e in OrderStatus])}"
        )
    
    order.status = new_status
    db.add(order)
    db.commit()
    db.refresh(order)
    
    return order 