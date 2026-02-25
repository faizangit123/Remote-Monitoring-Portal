"""
Database Connection and Session Management
This file sets up the connection to SQLite database and creates database sessions
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# ==============================================
# Create Database Engine
# ==============================================

engine = create_engine(
    settings.DATABASE_URL,
    # SQLite-specific settings
    connect_args={"check_same_thread": False},
    
    echo=False

)

# ==============================================
# Create Session Factory
# ==============================================

SessionLocal = sessionmaker(
    autocommit=False,
    
    autoflush=False,
    
    bind=engine
)


# ==============================================
# Create Base Class for Models
# ==============================================

Base = declarative_base()

# ==============================================
# Database Session Dependency
# ==============================================

def get_db():
    db = SessionLocal()  # Create new session
    try:
        yield db  # Provide session to route function
    finally:
        db.close()  # Always close session (even if error)


# ==============================================
# Initialize Database
# ==============================================

def init_db():
    # Import all models so they are registered with Base
    from . import models
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


# Testing function
if __name__ == "__main__":
    print("Database configuration:")
    print(f"Database URL: {settings.DATABASE_URL}")
    print(f"Engine: {engine}")
    print("Creating database tables...")
    init_db()