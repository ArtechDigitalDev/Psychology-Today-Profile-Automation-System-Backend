"""
profile_service.py
Service for managing Psychology Today profiles (CRUD operations).
"""
from sqlalchemy.orm import Session
from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate
from typing import List, Optional

def create_profile(db: Session, data: ProfileCreate) -> Profile:
    """Create a new profile with encrypted password."""
    profile = Profile(pt_username=data.pt_username, is_active=data.is_active, notes=data.notes)
    profile.set_password(data.password)
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def get_profile(db: Session, profile_id: int) -> Optional[Profile]:
    """Retrieve a profile by ID."""
    return db.query(Profile).filter(Profile.profile_id == profile_id).first()

def get_profile_by_username(db: Session, pt_username: str) -> Optional[Profile]:
    """Retrieve a profile by PT username."""
    return db.query(Profile).filter(Profile.pt_username == pt_username).first()

def update_profile(db: Session, profile_id: int, data: ProfileUpdate) -> Optional[Profile]:
    """Update a profile's fields."""
    print("data-", data)
    print("profile_id-", profile_id)
    print("db-", db)
    profile = get_profile(db, profile_id)
    if not profile:
        return None
    if data.pt_username:
        profile.pt_username = data.pt_username
    if data.password:
        profile.set_password(data.password)
    if data.is_active is not None:
        profile.is_active = data.is_active
    if data.status is not None:
        profile.status = data.status
    if data.notes is not None:
        profile.notes = data.notes
    if data.next_run_at is not None:
        profile.next_run_at = data.next_run_at
    db.commit()
    db.refresh(profile)
    return profile

def delete_profile(db: Session, profile_id: int) -> bool:
    """Delete a profile by ID."""
    profile = get_profile(db, profile_id)
    if profile:
        try:
            # First delete related update logs to avoid foreign key constraint violation
            from app.models.update_log import UpdateLog
            update_logs = db.query(UpdateLog).filter(UpdateLog.profile_id == profile_id).all()
            for log in update_logs:
                db.delete(log)
            
            # Then delete the profile
            db.delete(profile)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            print(f"Error deleting profile {profile_id}: {str(e)}")
            raise
    return False

def list_profiles(db: Session) -> List[Profile]:
    """List all profiles."""
    return db.query(Profile).all() 