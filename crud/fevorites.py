from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from auth import get_password_hash
from models import fevorites, menu, restaurants # For hashing passwords


# --- Favorite CRUD Operations ---
def get_favorite(db: Session, user_id: int, restaurant_id: int):
    """Checks if a restaurant is favorited by a user."""
    return db.query(fevorites.Favorite).filter(
        fevorites.Favorite.user_id == user_id,
        fevorites.Favorite.restaurant_id == restaurant_id
    ).first()

def get_user_favorites(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """Fetches all favorite restaurants for a user."""
    return db.query(fevorites.Favorite).filter(fevorites.Favorite.user_id == user_id).offset(skip).limit(limit).all()

def add_favorite(db: Session, user_id: int, restaurant_id: int):
    """Adds a restaurant to user's favorites."""
    db_favorite = fevorites.Favorite(user_id=user_id, restaurant_id=restaurant_id)
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite

def remove_favorite(db: Session, user_id: int, restaurant_id: int):
    """Removes a restaurant from user's favorites."""
    db_favorite = db.query(fevorites.Favorite).filter(
        fevorites.Favorite.user_id == user_id,
        fevorites.Favorite.restaurant_id == restaurant_id
    ).first()
    if db_favorite:
        db.delete(db_favorite)
        db.commit()
        return True
    return False

