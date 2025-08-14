"""
db.py
Database utility for SQLAlchemy session management.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# Create SQLAlchemy engine and session factory
engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    Dependency for FastAPI endpoints to provide a database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 