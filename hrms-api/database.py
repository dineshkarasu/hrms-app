"""
Database configuration and session management for HRMS
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os
from typing import Generator
from models.database_models import Base

# Database connection configuration
# Uses DATABASE_URL from environment variable (REQUIRED)
# No fallback values for security - environment must be configured
ENVIRONMENT = os.getenv("ENVIRONMENT", "dev").upper()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL environment variable is not set. "
        "Please configure your environment variables. "
        "See .env.example for reference."
    )

print(f"📊 Connecting to {ENVIRONMENT} database")
print(f"🔗 Database URL: {DATABASE_URL.split('@')[0]}@****")

# Create engine
# For PostgreSQL in production
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL debugging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session
    Use this in FastAPI route dependencies
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables
    Call this on application startup
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database tables created successfully in {ENVIRONMENT} environment")


def drop_db():
    """
    Drop all tables - use with caution!
    Only for development/testing
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️ All database tables dropped")
