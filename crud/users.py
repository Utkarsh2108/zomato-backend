# --- User CRUD Operations ---
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from auth import get_password_hash
from models import users
from schemas.users import UserCreate, UserUpdate

def get_user(db: Session, user_id: int):
    """Fetches a user by their ID."""
    return db.query(users.User).filter(users.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    """Fetches a user by their email."""
    return db.query(users.User).filter(users.User.email == email).first()

def create_user(db: Session, user: UserCreate):
    """Creates a new user in the database."""
    hashed_password = get_password_hash(user.password)
    db_user = users.User(
        email=user.email,
        name=user.name,
        phone=user.phone,
        hashed_password=hashed_password,
        role=users.UserRole.CUSTOMER # Default role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """Updates an existing user's information."""
    db_user = db.query(users.User).filter(users.User.id == user_id).first()
    if not db_user:
        return None
    
    # Update fields from the schema if they are provided
    update_data = user_update.model_dump(exclude_unset=True) 
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    """Deletes a user from the database."""
    db_user = db.query(users.User).filter(users.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False