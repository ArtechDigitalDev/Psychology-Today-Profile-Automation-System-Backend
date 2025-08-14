"""
profile.py
Pydantic schemas for Profile input/output.
"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ProfileCreate(BaseModel):
    pt_username: str
    password: str
    is_active: Optional[bool] = True
    notes: Optional[str] = None

class ProfileUpdate(BaseModel):
    pt_username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    status: Optional[str] = None
    notes: Optional[str] = None
    next_run_at: Optional[datetime] = None

class ProfileOut(BaseModel):
    profile_id: int
    pt_username: str
    is_active: bool
    status: Optional[str]
    last_run_at: Optional[datetime]
    last_success_at: Optional[datetime]
    next_run_at: Optional[datetime]
    notes: Optional[str]

    class Config:
        from_attributes = True 