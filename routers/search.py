# routers/search.py

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas.menu import MenuItemResponse
from schemas.restaurants import RestaurantResponse
from crud.search import search_restaurants_and_dishes as crud_search

# Import custom exceptions
from exceptions import (
    SearchException,
    InvalidSearchParametersException
)

router = APIRouter(
    prefix="/search",
    tags=["Search & Filters"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=dict)
def search_endpoint(
    query: Optional[str] = Query(None, description="Search keyword for restaurants or dishes"),
    cuisine: Optional[str] = Query(None, description="Filter restaurants by cuisine"),
    min_rating: Optional[float] = Query(None, ge=0.0, le=5.0, description="Filter restaurants by minimum rating (0.0 to 5.0)"),
    is_open: Optional[bool] = Query(None, description="Filter restaurants by open status (Requires further implementation for time-based checks)"),
    is_active: Optional[bool] = Query(True, description="Filter restaurants by active status"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search restaurants and dishes by keyword and apply various filters.
    
    - **query**: Keyword to search in restaurant names/cuisines or dish names/descriptions.
    - **cuisine**: Filter restaurants by specific cuisine (e.g., "Italian", "Indian").
    - **min_rating**: Filter restaurants by a minimum average rating (e.g., 4.0).
    - **is_open**: (Placeholder) Filter restaurants that are currently open. Requires time-based logic.
    - **is_active**: Filter restaurants that are active (default: True).
    """
    
    # Validate search parameters
    if skip < 0:
        raise InvalidSearchParametersException("Skip parameter must be non-negative")
    
    if limit <= 0 or limit > 1000:
        raise InvalidSearchParametersException("Limit parameter must be between 1 and 1000")
    
    if min_rating is not None and (min_rating < 0.0 or min_rating > 5.0):
        raise InvalidSearchParametersException("Minimum rating must be between 0.0 and 5.0")
    
    try:
        restaurants, menu_items = crud_search(
            db,
            query=query,
            cuisine=cuisine,
            min_rating=min_rating,
            is_open=is_open,
            is_active=is_active,
            skip=skip,
            limit=limit
        )

        # Convert SQLAlchemy models to Pydantic schemas for response
        restaurants_response = [RestaurantResponse.from_orm(r) for r in restaurants]
        menu_items_response = [MenuItemResponse.from_orm(m) for m in menu_items]

        return {
            "restaurants": restaurants_response,
            "menu_items": menu_items_response
        }
    
    except Exception as e:
        # If it's already a custom exception, re-raise it
        if isinstance(e, (SearchException, InvalidSearchParametersException)):
            raise
        # Otherwise, wrap it in a SearchException
        raise SearchException(f"Search operation failed: {str(e)}")