from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class Restaurant(Base):
    """
    SQLAlchemy model for the 'restaurants' table.
    Stores information about restaurants.
    """
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    phone = Column(String, unique=True, nullable=True)
    cuisine = Column(String, index=True)
    rating = Column(Float, default=0.0) # Average rating calculated from reviews
    opening_hours = Column(String) # e.g., "9:00 AM - 10:00 PM"
    is_active = Column(Boolean, default=True) # If restaurant is operational
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    menu_items = relationship("MenuItem", back_populates="restaurant")
    orders = relationship("Order", back_populates="restaurant")
    reviews = relationship("Review", back_populates="restaurant")
    favorites = relationship("Favorite", back_populates="restaurant")