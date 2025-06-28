from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from auth import get_password_hash
from models import menu # For hashing passwords
from schemas.menu import MenuItemCreate, MenuItemUpdate

# --- MenuItem CRUD Operations ---
def get_menu_items_by_restaurant(db: Session, restaurant_id: int, skip: int = 0, limit: int = 100):
    """Fetches menu items for a specific restaurant."""
    return db.query(menu.MenuItem).filter(menu.MenuItem.restaurant_id == restaurant_id).offset(skip).limit(limit).all()

def get_menu_item(db: Session, item_id: int):
    """Fetches a menu item by its ID."""
    return db.query(menu.MenuItem).filter(menu.MenuItem.id == item_id).first()

def create_menu_item(db: Session, menu_item: MenuItemCreate, restaurant_id: int):
    """Creates a new menu item for a given restaurant."""
    db_menu_item = menu.MenuItem(
        restaurant_id=restaurant_id,
        name=menu_item.name,
        description=menu_item.description,
        price=menu_item.price,
        is_available=menu_item.is_available,
        category=menu_item.category
    )
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

def update_menu_item(db: Session, item_id: int, menu_item_update: MenuItemUpdate):
    """Updates an existing menu item."""
    db_menu_item = db.query(menu.MenuItem).filter(menu.MenuItem.id == item_id).first()
    if not db_menu_item:
        return None
    
    update_data = menu_item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_menu_item, key, value)
    
    db.add(db_menu_item)
    db.commit()
    db.refresh(db_menu_item)
    return db_menu_item

def delete_menu_item(db: Session, item_id: int):
    """Deletes a menu item."""
    db_menu_item = db.query(menu.MenuItem).filter(menu.MenuItem.id == item_id).first()
    if db_menu_item:
        db.delete(db_menu_item)
        db.commit()
        return True
    return False