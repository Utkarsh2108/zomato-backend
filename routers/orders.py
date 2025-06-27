# routers/orders.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from crud.orders import create_order, get_all_orders, get_order, get_user_orders, cancel_order
import models.orders
import schemas, crud, models
from database import get_db
from auth import get_current_user, get_current_admin_user
import schemas.orders
import schemas.users
from exceptions import (
    OrderNotFoundException,
    OrderAccessDeniedException,
    OrderNotCancellableException,
    DatabaseException,
    ValidationException,
    EmptyCartException,
    InvalidOrderStatusException
)

router = APIRouter(
    prefix="/orders",
    tags=["Orders"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.orders.OrderResponse, status_code=201)
async def place_order(
    order: schemas.orders.OrderCreate,
    current_user: schemas.users.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Place a new order.
    Requires authentication.
    """
    try:
        # Validate order has items
        if not hasattr(order, 'order_items') or not order.order_items:
            raise EmptyCartException()
        
        db_order = create_order(db=db, order=order, user_id=current_user.id)
        if not db_order:
            raise DatabaseException("Failed to create order")
        return db_order
        
    except ValueError as e:
        raise ValidationException(str(e))
    except Exception as e:
        if isinstance(e, (EmptyCartException, ValidationException, DatabaseException)):
            raise
        raise DatabaseException(f"Error creating order: {str(e)}")

@router.get("/my/", response_model=List[schemas.orders.OrderResponse])
async def view_my_orders(
    skip: int = 0, limit: int = 100,
    current_user: schemas.users.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    View orders placed by the authenticated user.
    Requires authentication.
    """
    try:
        orders = get_user_orders(db, user_id=current_user.id, skip=skip, limit=limit)
        return orders
    except Exception as e:
        raise DatabaseException(f"Error retrieving user orders: {str(e)}")

@router.get("/{order_id}", response_model=schemas.orders.OrderResponse)
async def get_order_details(
    order_id: int,
    current_user: schemas.users.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get details of a specific order.
    Accessible by the user who placed the order or by an admin.
    """
    try:
        db_order = get_order(db, order_id=order_id)
        if not db_order:
            raise OrderNotFoundException(order_id)
        
        if db_order.user_id != current_user.id and current_user.role != models.UserRole.ADMIN:
            raise OrderAccessDeniedException(order_id)
        
        return db_order
    except Exception as e:
        if isinstance(e, (OrderNotFoundException, OrderAccessDeniedException)):
            raise
        raise DatabaseException(f"Error retrieving order details: {str(e)}")

@router.put("/{order_id}/cancel", response_model=schemas.orders.OrderResponse)
async def cancel_order_endpoint(
    order_id: int,
    current_user: schemas.users.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Cancel an order (only if status is pending).
    Accessible only by the user who placed the order.
    """
    try:
        db_order = get_order(db, order_id=order_id)
        if not db_order:
            raise OrderNotFoundException(order_id)
        
        if db_order.user_id != current_user.id:
            raise OrderAccessDeniedException(order_id)
        
        if db_order.status != models.OrderStatus.PENDING:
            raise OrderNotCancellableException(order_id, db_order.status.value)

        cancelled_order = crud.orders.cancel_order(db, order_id=order_id)
        if not cancelled_order:
            raise DatabaseException("Failed to cancel order")
        
        return cancelled_order
        
    except Exception as e:
        if isinstance(e, (OrderNotFoundException, OrderAccessDeniedException, OrderNotCancellableException, DatabaseException)):
            raise
        raise DatabaseException(f"Error canceling order: {str(e)}")

@router.get("/admin/", response_model=List[schemas.orders.OrderResponse])
async def admin_view_all_orders(
    skip: int = 0, limit: int = 100,
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Admin view of all orders.
    Requires admin authentication.
    """
    try:
        orders = get_all_orders(db, skip=skip, limit=limit)
        return orders
    except Exception as e:
        raise DatabaseException(f"Error retrieving all orders: {str(e)}")

@router.put("/{order_id}/status", response_model=schemas.orders.OrderResponse)
async def update_order_status(
    order_id: int,
    new_status: models.orders.OrderStatus, # FastAPI will automatically validate against enum
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Admin updates an order's status.
    Requires admin authentication.
    """
    try:
        # Validate status transition logic (optional enhancement)
        db_order = get_order(db, order_id=order_id)
        if not db_order:
            raise OrderNotFoundException(order_id)
        
        # Update order status
        updated_order = crud.orders.update_order_status(db, order_id, new_status)
        if not updated_order:
            raise DatabaseException("Failed to update order status")
            
        return updated_order
        
    except Exception as e:
        if isinstance(e, (OrderNotFoundException, InvalidOrderStatusException, DatabaseException)):
            raise
        raise DatabaseException(f"Error updating order status: {str(e)}")