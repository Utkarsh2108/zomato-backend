from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from models import orders 
from models import menu
from schemas.orders import OrderCreate

# --- Order CRUD Operations ---
def get_order(db: Session, order_id: int):
    """Fetches an order by ID."""
    return db.query(orders.Order).filter(orders.Order.id == order_id).first()

def get_user_orders(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Fetches all orders for a specific user."""
    return db.query(orders.Order).filter(orders.Order.user_id == user_id).offset(skip).limit(limit).all()

def get_all_orders(db: Session, skip: int = 0, limit: int = 100):
    """Fetches all orders (admin view)."""
    return db.query(orders.Order).offset(skip).limit(limit).all()

def create_order(db: Session, order: OrderCreate, user_id: int):
    """Creates a new order."""
    # Validate menu items and calculate total price
    total_price = 0.0
    processed_items = []
    
    # Fetch all menu items for the restaurant in one go to minimize DB queries
    restaurant_menu_items = db.query(menu.MenuItem).filter(
        menu.MenuItem.restaurant_id == order.restaurant_id
    ).all()
    menu_item_map = {item.id: item for item in restaurant_menu_items}

    for item_data in order.items:
        menu_item = menu_item_map.get(item_data.menu_item_id)
        if not menu_item or not menu_item.is_available:
            raise ValueError(f"Menu item with ID {item_data.menu_item_id} not found or not available in this restaurant.")
        total_price += menu_item.price * item_data.quantity
        processed_items.append({"menu_item_id": item_data.menu_item_id, "quantity": item_data.quantity, "price_at_order": menu_item.price})

    db_order = orders.Order(
        user_id=user_id,
        restaurant_id=order.restaurant_id,
        items=processed_items,
        total_price=total_price,
        status=orders.OrderStatus.PENDING
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def cancel_order(db: Session, order_id: int):
    """Cancels an order if it's in pending status."""
    db_order = db.query(orders.Order).filter(orders.Order.id == order_id).first()
    if not db_order:
        return None
    if db_order.status == orders.OrderStatus.PENDING:
        db_order.status = orders.OrderStatus.CANCELLED
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    return None # Order cannot be cancelled

def update_order_status(db: Session, order_id: int, new_status: orders.OrderStatus):
    """Updates the status of an order (typically by admin)."""
    db_order = db.query(orders.Order).filter(orders.Order.id == order_id).first()
    if not db_order:
        return None
    db_order.status = new_status
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order
