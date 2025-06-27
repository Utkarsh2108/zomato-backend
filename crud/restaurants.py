from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from models import restaurants 
from schemas.restaurants import RestaurantCreate, RestaurantUpdate

# --- Restaurant CRUD Operations ---
def get_restaurants(db: Session, skip: int = 0, limit: int = 100):
    """Fetches a list of all restaurants."""
    return db.query(restaurants.Restaurant).offset(skip).limit(limit).all()

def get_restaurant(db: Session, restaurant_id: int):
    """Fetches a restaurant by its ID."""
    return db.query(restaurants.Restaurant).filter(restaurants.Restaurant.id == restaurant_id).first()

def create_restaurant(db: Session, restaurant: RestaurantCreate):
    """Creates a new restaurant."""
    db_restaurant = restaurants.Restaurant(
        name=restaurant.name,
        address=restaurant.address,
        phone=restaurant.phone,
        cuisine=restaurant.cuisine,
        opening_hours=restaurant.opening_hours,
        is_active=restaurant.is_active
    )
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def update_restaurant(db: Session, restaurant_id: int, restaurant_update: RestaurantUpdate):
    """Updates an existing restaurant's information."""
    db_restaurant = db.query(restaurants.Restaurant).filter(restaurants.Restaurant.id == restaurant_id).first()
    if not db_restaurant:
        return None
    
    update_data = restaurant_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_restaurant, key, value)
    
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant

def delete_restaurant(db: Session, restaurant_id: int):
    """Deletes a restaurant from the database."""
    db_restaurant = db.query(restaurants.Restaurant).filter(restaurants.Restaurant.id == restaurant_id).first()
    if db_restaurant:
        db.delete(db_restaurant)
        db.commit()
        return True
    return False
