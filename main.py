# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import engine, Base, get_db
import models
from routers import users, restaurants, orders, reviews, favorites, search
import os
from dotenv import load_dotenv
from exception_handlers import register_exception_handlers
import exceptions

# Load environment variables
load_dotenv()

# Create all database tables defined in models.py
# This is for initial setup. In production, use Alembic for migrations.
def create_tables():
    """
    Creates all database tables. This should ideally be handled by Alembic in production.
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

# Initialize FastAPI app
app = FastAPI(
    title="Zomato Clone Backend API")

# Register exception handlers
register_exception_handlers(app)

@app.get("/healthcheckpoint", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "message": "Zomato Clone API is running successfully"
    }

# Include routers
app.include_router(users.router)
app.include_router(restaurants.router)
app.include_router(orders.router)
app.include_router(reviews.router)
app.include_router(favorites.router)
app.include_router(search.router)

# Optional: Create tables on startup (for development)
# In production, use Alembic migrations instead
