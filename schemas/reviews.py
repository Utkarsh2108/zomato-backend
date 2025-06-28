from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Review Schemas ---
class ReviewBase(BaseModel):
    """Base schema for review properties."""
    rating: float = Field(..., ge=1, le=5) # Rating must be between 1 and 5
    comment: Optional[str] = None

class ReviewCreate(ReviewBase):
    """Schema for adding a new review."""
    restaurant_id: int
    # user_id will be derived from authenticated user

class ReviewUpdate(ReviewBase):
    """Schema for updating a review."""
    pass

class ReviewResponse(ReviewBase):
    """Schema for review data returned in API responses."""
    id: int
    user_id: int
    restaurant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True