"""
auth.py
Pydantic schemas for authentication.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class UserLogin(BaseModel):
    """Schema for user login request."""
    username: str
    password: str

class Token(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"

class UserOut(BaseModel):
    """Schema for user output (without password)."""
    user_id: int
    username: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None 

class UserCreate(BaseModel):
    """Schema for user creation request."""
    username: str
    password: str 