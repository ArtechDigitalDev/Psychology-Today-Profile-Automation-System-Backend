"""
create_tables.py
Script to create all database tables for the application.
Run this once before using the API.
"""
from app.models.user import Base
from app.utils.db import engine

# Import all models to ensure they are registered
from app.models.user import User
from app.models.profile import Profile
from app.models.update_log import UpdateLog

# Create all tables at once (SQLAlchemy will handle the order)
Base.metadata.create_all(bind=engine)

print("All tables created!") 