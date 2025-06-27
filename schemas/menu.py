from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# --- Menu Item Schemas ---
class MenuItemBase(BaseModel):
    """Base schema for menu item properties."""
    name: str
    description: Optional[str] = None
    price: float = Field(..., gt=0) # Price must be greater than 0
    is_available: Optional[bool] = True
    category: str

class MenuItemCreate(MenuItemBase):
    """Schema for creating a new menu item."""
    restaurant_id: Optional[int] = None # Will be set by path parameter

class MenuItemUpdate(BaseModel):
    """Schema for updating menu item information."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_available: Optional[bool] = None
    category: Optional[str] = None

class MenuItemResponse(MenuItemBase):
    """Schema for menu item data returned in API responses."""
    id: int
    restaurant_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True