"""
update_log.py
SQLAlchemy model for tracking detailed update logs of profile maintenance.
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

# Use the same Base as other models
from app.models.user import Base

class UpdateLog(Base):
    __tablename__ = "update_logs"

    log_id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("profiles.profile_id"), nullable=False)
    executed_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    outcome = Column(String(20), nullable=False)  # 'Success', 'Failure', 'Warning'
    duration_ms = Column(Integer)  # Duration in milliseconds
    fields_edited = Column(JSON)  # JSON object of edited fields
    log_details = Column(Text)  # Error messages or additional details
    
    # Relationship with Profile
    profile = relationship("Profile", back_populates="update_logs")
    
    def __repr__(self):
        return f"<UpdateLog(log_id={self.log_id}, profile_id={self.profile_id}, outcome={self.outcome}, executed_at={self.executed_at})>"
    
    @classmethod
    def create_log(cls, db, profile_id: int, outcome: str, duration_ms: int = None, 
                    fields_edited: dict = None, log_details: str = None):
        """Create a new update log entry."""
        log_entry = cls(
            profile_id=profile_id,
            outcome=outcome,
            duration_ms=duration_ms,
            fields_edited=fields_edited,
            log_details=log_details,
            executed_at=datetime.now(timezone.utc)
        )
        db.add(log_entry)
        db.commit()
        db.refresh(log_entry)
        return log_entry
    
    @classmethod
    def get_profile_logs(cls, db, profile_id: int, limit: int = 50):
        """Get recent logs for a specific profile."""
        return db.query(cls).filter(
            cls.profile_id == profile_id
        ).order_by(cls.executed_at.desc()).limit(limit).all()
    
    @classmethod
    def get_recent_logs(cls, db, limit: int = 100):
        """Get recent logs across all profiles."""
        return db.query(cls).order_by(cls.executed_at.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_outcome(cls, db, outcome: str, limit: int = 50):
        """Get logs filtered by outcome (Success, Failure, Warning)."""
        return db.query(cls).filter(
            cls.outcome == outcome
        ).order_by(cls.executed_at.desc()).limit(limit).all()
    
    @classmethod
    def get_logs_by_date_range(cls, db, start_date: datetime, end_date: datetime):
        """Get logs within a specific date range."""
        return db.query(cls).filter(
            cls.executed_at >= start_date,
            cls.executed_at <= end_date
        ).order_by(cls.executed_at.desc()).all() 