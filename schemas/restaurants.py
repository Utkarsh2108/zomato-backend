from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Restaurant Schemas ---
class RestaurantBase(BaseModel):
    """Base schema for restaurant properties."""
    name: str
    address: str
    phone: Optional[str] = None
    cuisine: str
    opening_hours: str
    is_active: Optional[bool] = True

class RestaurantCreate(RestaurantBase):
    """Schema for creating a new restaurant."""
    pass

class RestaurantUpdate(BaseModel):
    """Schema for updating restaurant information."""
    name: Optional[str] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    cuisine: Optional[str] = None
    opening_hours: Optional[str] = None
    is_active: Optional[bool] = None
    rating: Optional[float] = None # Rating can be updated via reviews, but included for admin flexibility


class RestaurantResponse(RestaurantBase):
    """Schema for restaurant data returned in API responses."""
    id: int
    rating: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True