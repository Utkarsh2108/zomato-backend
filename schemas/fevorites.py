from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Favorite Schemas ---
class FavoriteCreate(BaseModel):
    """Schema for adding a favorite restaurant."""
    restaurant_id: int
    # user_id will be derived from authenticated user

class FavoriteResponse(BaseModel):
    """Schema for favorite data returned in API responses."""
    id: int
    user_id: int
    restaurant_id: int
    created_at: datetime

    class Config:
        from_attributes = True