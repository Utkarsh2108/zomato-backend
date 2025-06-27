from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.users import UserRole

# --- User creation Schemas ---
# These schemas are used for user registration and profile management.
class UserBase(BaseModel):
    """Base schema for user properties."""
    email: EmailStr
    name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    """Schema for creating a new user (registration)."""
    password: str = Field(..., min_length=6) # Password required for creation

class UserUpdate(BaseModel):
    """Schema for updating user information."""
    name: Optional[str] = None
    phone: Optional[str] = None
    # Email and password are not directly updatable via this schema (handled separately or not allowed)
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None
    
# --- User authentication Schemas ---
# These schemas are used for user login and authentication processes.
class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    """Schema for user data stored in the database, including sensitive fields."""
    id: int
    hashed_password: str
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True # Allows SQLAlchemy models to be converted to Pydantic models

class UserResponse(UserBase):
    """Schema for user data returned in API responses (excluding sensitive fields like password hash)."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        

# --- Token Schemas (for authentication) ---
# These schemas are used for JWT token generation and validation.
class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    """Schema for data extracted from JWT token."""
    email: Optional[str] = None
    role: Optional[UserRole] = None
    user_id: Optional[int] = None # Added user_id to TokenData