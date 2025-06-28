from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from auth import get_password_hash
from models import reviews # For hashing passwords
from schemas.reviews import ReviewCreate, ReviewUpdate

# --- Review CRUD Operations ---
def get_review(db: Session, review_id: int):
    """Fetches a review by ID."""
    return db.query(reviews.Review).filter(reviews.Review.id == review_id).first()

def get_reviews_by_restaurant(db: Session, restaurant_id: int, skip: int = 0, limit: int = 100):
    """Fetches all reviews for a specific restaurant."""
    return db.query(reviews.Review).filter(reviews.Review.restaurant_id == restaurant_id).offset(skip).limit(limit).all()

def create_review(db: Session, review: ReviewCreate, user_id: int):
    """Adds a new review for a restaurant."""
    # Ensure order is completed for review (bonus requirement)
    # This check would ideally involve finding a completed order by the user for this restaurant
    # For simplicity, we skip this check here, but it should be added in the router.
    
    db_review = reviews.Review(
        user_id=user_id,
        restaurant_id=review.restaurant_id,
        rating=review.rating,
        comment=review.comment
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def update_review(db: Session, review_id: int, review_update: ReviewUpdate):
    """Updates an existing review."""
    db_review = db.query(reviews.Review).filter(reviews.Review.id == review_id).first()
    if not db_review:
        return None
    
    update_data = review_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_review, key, value)
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review

def delete_review(db: Session, review_id: int):
    """Deletes a review."""
    db_review = db.query(reviews.Review).filter(reviews.Review.id == review_id).first()
    if db_review:
        db.delete(db_review)
        db.commit()
        return True
    return False