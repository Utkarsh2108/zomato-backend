# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database URL is fetched from environment variables
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class to get a database session.
# Each instance of SessionLocal will be a database session.
# The sessionmaker creates a configured Session class.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models. All SQLAlchemy models will inherit from this.
Base = declarative_base()

# Dependency to get the database session
def get_db():
    """
    Dependency function to provide a database session.
    It yields a session that can be used in FastAPI path operations.
    The session is automatically closed after the request is finished.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

