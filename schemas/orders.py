import enum
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# Define Enum for order status
class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    
# --- Order Schemas ---
class OrderItemSchema(BaseModel):
    """Schema for individual item within an order."""
    menu_item_id: int
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    """Schema for placing a new order."""
    restaurant_id: int
    items: List[OrderItemSchema] # List of menu item IDs and quantities

class OrderUpdate(BaseModel):
    """Schema for updating an existing order (e.g., status by admin)."""
    status: Optional[OrderStatus] = None
    # For user cancelling an order, a specific endpoint is better (e.g., PUT /orders/{id}/cancel)

class OrderResponse(BaseModel):
    """Schema for order data returned in API responses."""
    id: int
    user_id: int
    restaurant_id: int
    items: List[Dict[str, Any]] # Will be parsed from JSON (list of dicts)
    status: OrderStatus
    total_price: float
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True