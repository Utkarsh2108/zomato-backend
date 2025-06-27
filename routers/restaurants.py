# routers/restaurants.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

import schemas, crud, models
from database import get_db
from auth import get_current_user, get_current_admin_user
import schemas.menu
import schemas.restaurants
import schemas.users
from crud.restaurants import get_restaurant, get_restaurants, delete_restaurant, update_restaurant
from crud.menu import create_menu_item, get_menu_items_by_restaurant

# Import custom exceptions
from exceptions import (
    RestaurantNotFoundException,
    MenuItemNotFoundException,
    RestaurantInactiveException
)

router = APIRouter(
    prefix="/restaurants",
    tags=["Restaurants"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[schemas.restaurants.RestaurantResponse])
def read_restaurants(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all restaurants.
    """
    restaurants = get_restaurants(db, skip=skip, limit=limit)
    return restaurants

@router.post("/", response_model=schemas.restaurants.RestaurantResponse, status_code=status.HTTP_201_CREATED)
def create_restaurant(
    restaurant: schemas.restaurants.RestaurantCreate,
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Create a new restaurant.
    Requires admin authentication.
    """
    # You might want to add a check here if a restaurant with the same name/address already exists
    return crud.restaurants.create_restaurant(db=db, restaurant=restaurant)

@router.get("/{restaurant_id}", response_model=schemas.restaurants.RestaurantResponse)
def read_restaurant(restaurant_id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific restaurant by ID.
    """
    db_restaurant = get_restaurant(db, restaurant_id=restaurant_id)
    if db_restaurant is None:
        raise RestaurantNotFoundException(restaurant_id)
    return db_restaurant

@router.put("/{restaurant_id}", response_model=schemas.restaurants.RestaurantResponse)
def update_restaurant_endpoint(
    restaurant_id: int,
    restaurant: schemas.restaurants.RestaurantUpdate,
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Update an existing restaurant's information.
    Requires admin authentication.
    """
    db_restaurant = crud.restaurants.update_restaurant(db, restaurant_id=restaurant_id, restaurant_update=restaurant)
    if db_restaurant is None:
        raise RestaurantNotFoundException(restaurant_id)
    return db_restaurant

@router.delete("/{restaurant_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_restaurant_endpoint(
    restaurant_id: int,
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Delete a restaurant.
    Requires admin authentication.
    """
    success = delete_restaurant(db, restaurant_id=restaurant_id)
    if not success:
        raise RestaurantNotFoundException(restaurant_id)
    return

# --- Menu Item Endpoints (Admin only for POST, PUT, DELETE) ---

@router.get("/{restaurant_id}/menu/", response_model=List[schemas.menu.MenuItemResponse])
def read_menu_items_for_restaurant(restaurant_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all menu items for a specific restaurant.
    """
    db_restaurant = get_restaurant(db, restaurant_id)
    if not db_restaurant:
        raise RestaurantNotFoundException(restaurant_id)
    menu_items = get_menu_items_by_restaurant(db, restaurant_id=restaurant_id, skip=skip, limit=limit)
    return menu_items

@router.post("/{restaurant_id}/menu/", response_model=schemas.menu.MenuItemResponse, status_code=status.HTTP_201_CREATED)
def create_menu_item_for_restaurant(
    restaurant_id: int,
    menu_item: schemas.menu.MenuItemCreate,
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Add a new menu item to a restaurant.
    Requires admin authentication.
    """
    db_restaurant = get_restaurant(db, restaurant_id)
    if not db_restaurant:
        raise RestaurantNotFoundException(restaurant_id)
    return create_menu_item(db=db, menu_item=menu_item, restaurant_id=restaurant_id)

@router.put("/menu/{item_id}", response_model=schemas.menu.MenuItemResponse)
def update_menu_item(
    item_id: int,
    menu_item: schemas.menu.MenuItemUpdate,
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Update an existing menu item.
    Requires admin authentication.
    """
    db_menu_item = crud.menu.update_menu_item(db, item_id=item_id, menu_item_update=menu_item)
    if db_menu_item is None:
        raise MenuItemNotFoundException(item_id)
    return db_menu_item

@router.delete("/menu/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_menu_item(
    item_id: int,
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Delete a menu item.
    Requires admin authentication.
    """
    success = crud.menu.delete_menu_item(db, item_id=item_id)
    if not success:
        raise MenuItemNotFoundException(item_id)
    return