# crud/search.py

from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from models import menu, restaurants


def search_restaurants_and_dishes(
    db: Session, 
    query: Optional[str] = None,
    cuisine: Optional[str] = None,
    min_rating: Optional[float] = None,
    is_open: Optional[bool] = None,
    is_active: Optional[bool] = True,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[restaurants.Restaurant], List[menu.MenuItem]]:
    """
    Searches restaurants and dishes based on keywords and filters.
    
    Returns:
        Tuple of (restaurants, menu_items)
    """
    restaurants_query = db.query(restaurants.Restaurant)
    menu_items_query = db.query(menu.MenuItem)

    # Apply active filter for restaurants
    if is_active is not None:
        restaurants_query = restaurants_query.filter(restaurants.Restaurant.is_active == is_active)
    
    # Apply search query
    if query:
        # Search in restaurant names and cuisines
        restaurants_query = restaurants_query.filter(
            or_(
                restaurants.Restaurant.name.ilike(f"%{query}%"),
                restaurants.Restaurant.cuisine.ilike(f"%{query}%")
            )
        )
        # Search in menu item names and descriptions
        menu_items_query = menu_items_query.filter(
            or_(
                menu.MenuItem.name.ilike(f"%{query}%"),
                menu.MenuItem.description.ilike(f"%{query}%")
            )
        )
    
    # Apply cuisine filter
    if cuisine:
        restaurants_query = restaurants_query.filter(
            restaurants.Restaurant.cuisine.ilike(f"%{cuisine}%")
        )
    
    # Apply minimum rating filter
    if min_rating is not None:
        restaurants_query = restaurants_query.filter(
            restaurants.Restaurant.rating >= min_rating
        )
    
    # Apply is_open filter (simplified - you may need more complex logic)
    # This assumes you have an 'is_open' field or you implement time-based logic
    if is_open is not None:
        # For now, this is a placeholder. You might want to implement
        # actual time-based checking against opening_hours
        # restaurants_query = restaurants_query.filter(restaurants.Restaurant.is_open == is_open)
        pass
    
    # Execute queries with pagination
    restaurants_result = restaurants_query.offset(skip).limit(limit).all()
    menu_items_result = menu_items_query.offset(skip).limit(limit).all()
    
    return restaurants_result, menu_items_result