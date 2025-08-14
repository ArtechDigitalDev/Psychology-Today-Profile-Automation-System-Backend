"""
update_log.py
Pydantic schemas for update log data validation.
"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class UpdateLogBase(BaseModel):
    """Base schema for update log."""
    profile_id: int
    outcome: str  # 'Success', 'Failure', 'Warning'
    duration_ms: Optional[int] = None
    fields_edited: Optional[Dict[str, Any]] = None
    log_details: Optional[str] = None

class UpdateLogCreate(UpdateLogBase):
    """Schema for creating a new update log."""
    pass

class UpdateLogOut(UpdateLogBase):
    """Schema for update log output."""
    log_id: int
    executed_at: datetime
    pt_username: Optional[str] = None  # Will be populated from profile
    
    class Config:
        from_attributes = True

class UpdateLogSummary(BaseModel):
    """Schema for update log summary statistics."""
    total_logs: int
    success_count: int
    failure_count: int
    nochange_count: int
    warning_count: int
    average_duration_ms: Optional[float] = None
    recent_logs: list[UpdateLogOut]
    
    class Config:
        from_attributes = True 