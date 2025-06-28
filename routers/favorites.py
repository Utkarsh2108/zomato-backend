# routers/favorites.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from auth import get_current_user
import crud
from crud.fevorites import add_favorite, get_favorite, get_user_favorites
from crud.restaurants import get_restaurant
import crud.restaurants
from database import get_db
import schemas
import schemas.fevorites
import schemas.restaurants
from exceptions import (
    RestaurantNotFoundException,
    DatabaseException
)


router = APIRouter(
    prefix="/favorites",
    tags=["Favorites"],
    responses={404: {"description": "Not found"}},
)

@router.post("/{restaurant_id}", response_model=schemas.fevorites.FavoriteResponse)
async def toggle_favorite(
    restaurant_id: int,
    current_user: schemas.users.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Toggle a restaurant as favorite/unfavorite for the authenticated user.
    If already favorited, it will be unfavorited. If not, it will be added.
    Requires authentication.
    """
    try:
        # Check if restaurant exists
        db_restaurant = get_restaurant(db, restaurant_id)
        if not db_restaurant:
            raise RestaurantNotFoundException(restaurant_id)

        existing_favorite = get_favorite(db, user_id=current_user.id, restaurant_id=restaurant_id)

        if existing_favorite:
            # If exists, remove it (unfavorite)
            crud.remove_favorite(db, user_id=current_user.id, restaurant_id=restaurant_id)
            # Return a custom success message for unfavorite
            return schemas.FavoriteResponse(
                id=existing_favorite.id,
                user_id=existing_favorite.user_id,
                restaurant_id=existing_favorite.restaurant_id,
                created_at=existing_favorite.created_at # Keep original creation time for response consistency
            )
        else:
            # If not exists, add it (favorite)
            new_favorite = add_favorite(db, user_id=current_user.id, restaurant_id=restaurant_id)
            if not new_favorite:
                raise DatabaseException("Failed to add restaurant to favorites")
            return new_favorite
            
    except Exception as e:
        if isinstance(e, (RestaurantNotFoundException, DatabaseException)):
            raise
        raise DatabaseException(f"Error toggling favorite: {str(e)}")

@router.get("/", response_model=List[schemas.restaurants.RestaurantResponse])
async def list_my_favorite_restaurants(
    skip: int = 0, limit: int = 100,
    current_user: schemas.users.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all favorite restaurants for the authenticated user.
    Requires authentication.
    """
    try:
        user_favorites = get_user_favorites(db, user_id=current_user.id, skip=skip, limit=limit)
        
        # Fetch full restaurant details for each favorite
        favorite_restaurants = []
        for fav in user_favorites:
            restaurant = crud.restaurants.get_restaurant(db, fav.restaurant_id)
            if restaurant:
                favorite_restaurants.append(schemas.restaurants.RestaurantResponse.from_orm(restaurant))
        
        return favorite_restaurants
        
    except Exception as e:
        raise DatabaseException(f"Error retrieving favorite restaurants: {str(e)}")