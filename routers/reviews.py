# routers/reviews.py

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from auth import get_current_user
import crud.restaurants
from crud.reviews import create_review, get_review, get_reviews_by_restaurant
import crud.reviews
from database import get_db
import schemas, crud, models
import schemas.reviews

# Import custom exceptions
from exceptions import (
    ReviewNotFoundException,
    ReviewAlreadyExistsException,
    ReviewNotAllowedException,
    ReviewAccessDeniedException,
    RestaurantNotFoundException
)

router = APIRouter(
    prefix="/reviews",
    tags=["Reviews"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=schemas.reviews.ReviewResponse, status_code=status.HTTP_201_CREATED)
async def add_review(
    review: schemas.reviews.ReviewCreate,
    current_user: schemas.users.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add a new review for a restaurant.
    Only for completed orders.
    Requires authentication.
    """
    # Check if the user has a completed order for this restaurant
    # This is a crucial "bonus requirement" check.
    # It requires iterating through user's orders to find a matching, completed order.
    user_completed_orders = db.query(models.Order).filter(
        models.Order.user_id == current_user.id,
        models.Order.restaurant_id == review.restaurant_id,
        models.Order.status == models.OrderStatus.DELIVERED # Only delivered orders can be reviewed
    ).first()

    if not user_completed_orders:
        raise ReviewNotAllowedException(review.restaurant_id)

    # Check if the user has already reviewed this restaurant (optional: prevent multiple reviews per user per restaurant)
    existing_review = db.query(models.Review).filter(
        models.Review.user_id == current_user.id,
        models.Review.restaurant_id == review.restaurant_id
    ).first()
    
    if existing_review:
        raise ReviewAlreadyExistsException(review.restaurant_id)

    db_review = create_review(db=db, review=review, user_id=current_user.id)
    
    # Optional: Update restaurant's average rating
    # This would involve recalculating the average rating for the restaurant after each new review.
    # For a real-world app, this might be handled by a background task or more sophisticated logic.
    
    return db_review

@router.get("/restaurant/{restaurant_id}", response_model=List[schemas.reviews.ReviewResponse])
def get_reviews_for_restaurant(restaurant_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all reviews for a specific restaurant.
    """
    reviews = get_reviews_by_restaurant(db, restaurant_id=restaurant_id, skip=skip, limit=limit)
    if not reviews and not crud.restaurants.get_restaurant(db, restaurant_id):
        raise RestaurantNotFoundException(restaurant_id)
    return reviews

@router.put("/{review_id}", response_model=schemas.reviews.ReviewResponse)
async def update_review(
    review_id: int,
    review_update: schemas.reviews.ReviewUpdate,
    current_user: schemas.users.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing review.
    Only accessible by the user who created the review.
    """
    db_review = get_review(db, review_id)
    if not db_review:
        raise ReviewNotFoundException(review_id)
    
    if db_review.user_id != current_user.id:
        raise ReviewAccessDeniedException(review_id)
    
    updated_review = crud.reviews.update_review(db, review_id=review_id, review_update=review_update)
    return updated_review

@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: int,
    current_user: schemas.users.UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a review.
    Only accessible by the user who created the review or by an admin.
    """
    db_review = get_review(db, review_id)
    if not db_review:
        raise ReviewNotFoundException(review_id)
    
    if db_review.user_id != current_user.id and current_user.role != models.UserRole.ADMIN:
        raise ReviewAccessDeniedException(review_id)
    
    success = crud.reviews.delete_review(db, review_id=review_id)
    if not success:
        # This should not happen if db_review was found, but handle it gracefully
        raise ReviewNotFoundException(review_id)
    return
