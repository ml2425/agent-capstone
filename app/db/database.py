"""Database setup and configuration."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os

# Create Base here to avoid circular import
Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./medical_mcq.db")
SESSION_DB_URL = os.getenv("SESSION_DB_URL", "sqlite:///./agent_sessions.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    # Import models here to ensure they're registered with Base
    from app.db import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

