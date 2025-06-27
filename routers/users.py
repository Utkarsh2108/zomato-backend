from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from crud import users as crud
from database import get_db
from auth import verify_password, create_access_token, get_current_user, get_current_admin_user
from datetime import timedelta
import os
from dotenv import load_dotenv
import models
import schemas
import schemas.users

# Import custom exceptions
from exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    InvalidCredentialsException,
    AuthenticationException
)

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

# Initialize HTTPBearer security scheme
security = HTTPBearer()

router = APIRouter(
    prefix="/users",
    tags=["Users & Authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post("/register/", response_model=schemas.users.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: schemas.users.UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    - **email**: User's email (must be unique).
    - **name**: User's name.
    - **password**: User's password (min 6 characters).
    - **phone**: Optional phone number.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise UserAlreadyExistsException(user.email)
    return crud.create_user(db=db, user=user)

@router.post("/login/", response_model=schemas.users.Token)
async def login_for_access_token(
    login_data: schemas.users.UserLogin, db: Session = Depends(get_db)
):
    """
    Authenticate user and get JWT access token.
    - **email**: User's email.
    - **password**: User's password.
    """
    user = crud.get_user_by_email(db, email=login_data.email)
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise InvalidCredentialsException()
    
    # Create an access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "role": user.role.value},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me/", response_model=schemas.users.UserResponse)
async def read_users_me(current_user: schemas.users.UserResponse = Depends(get_current_user)):
    """
    Retrieve current authenticated user's details.
    Requires authentication.
    """
    return current_user

@router.put("/me/", response_model=schemas.users.UserResponse)
async def update_users_me(
    user_update: schemas.users.UserUpdate, 
    current_user: schemas.users.UserResponse = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Update current authenticated user's details.
    Requires authentication.
    """
    db_user = crud.update_user(db, current_user.id, user_update)
    if not db_user:
        raise UserNotFoundException(user_id=current_user.id)
    return db_user

@router.get("/", response_model=List[schemas.users.UserResponse])
async def get_all_users(
    skip: int = 0, limit: int = 100,
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Retrieve all users.
    Requires admin authentication.
    """
    users = db.query(models.users.User).offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=schemas.users.UserResponse)
async def get_user_by_id(
    user_id: int, 
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Retrieve a user by ID.
    Requires admin authentication.
    """
    db_user = crud.get_user(db, user_id)
    if not db_user:
        raise UserNotFoundException(user_id=user_id)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_admin_user: schemas.users.UserResponse = Depends(get_current_admin_user), # Admin only
    db: Session = Depends(get_db)
):
    """
    Delete a user by ID.
    Requires admin authentication.
    """
    success = crud.delete_user(db, user_id)
    if not success:
        raise UserNotFoundException(user_id=user_id)
    return