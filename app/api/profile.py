"""
profile.py
FastAPI router for managing Psychology Today profiles (admin only).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.services.profile_service import (
    create_profile, get_profile, update_profile, delete_profile, list_profiles
)
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileOut
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.schemas.response import APIResponse

router = APIRouter(prefix="/profiles", tags=["Profiles"])

@router.post("/", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_profile_endpoint(
    profile_data: ProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check for duplicate pt_username
    existing = db.query(Profile).filter(Profile.pt_username == profile_data.pt_username).first()
    if existing:
        return APIResponse(success=False, message="Profile with this pt_username already exists.", data=None)
    print("current_user-", current_user)
    print("profile_data-", profile_data)
    profile = create_profile(db, profile_data)
    print("profile-", profile)
    return APIResponse(
        success=True, 
        message="Profile created successfully.", 
        data=ProfileOut.model_validate(profile))

@router.get("/", response_model=APIResponse)
def list_profiles_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    print("current_user-", current_user)
    profiles = list_profiles(db)
    return APIResponse(
        success=True, 
        message="Profiles fetched successfully.", 
        data=[ProfileOut.model_validate(p) for p in profiles]
        )

@router.get("/{profile_id}", response_model=APIResponse)
def get_profile_endpoint(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    profile = get_profile(db, profile_id)
    if not profile:
        return APIResponse(success=False, message="Profile not found.", data=None)
    return APIResponse(
        success=True, 
        message="Profile fetched successfully.", 
        data=ProfileOut.model_validate(profile)
        )

@router.put("/{profile_id}", response_model=APIResponse)
def update_profile_endpoint(
    profile_id: int,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if profile exists
    existing_profile = db.query(Profile).filter(Profile.profile_id == profile_id).first()
    if not existing_profile:
        return APIResponse(success=False, message="Profile not found.", data=None)
    
    # Check for duplicate pt_username if it's being updated
    if profile_data.pt_username and profile_data.pt_username != existing_profile.pt_username:
        duplicate = db.query(Profile).filter(
            Profile.pt_username == profile_data.pt_username,
            Profile.profile_id != profile_id
        ).first()
        if duplicate:
            return APIResponse(success=False, message="Profile with this pt_username already exists.", data=None)
    
    updated = update_profile(db, profile_id, profile_data)
    if not updated:
        return APIResponse(success=False, message="Profile not found.", data=None)
    return APIResponse(
        success=True, 
        message="Profile updated successfully.", 
        data=ProfileOut.model_validate(updated)
        )

@router.delete("/{profile_id}", response_model=APIResponse)
def delete_profile_endpoint(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Check if profile exists first
        profile = get_profile(db, profile_id)
        if not profile:
            return APIResponse(success=False, message="Profile not found.", data=None)
        
        # Delete the profile and related logs
        if delete_profile(db, profile_id):
            return APIResponse(
                success=True, 
                message=f"Profile '{profile.pt_username}' and all related logs deleted successfully.", 
                data=None
            )
        else:
            return APIResponse(success=False, message="Failed to delete profile.", data=None)
            
    except Exception as e:
        print(f"Error in delete_profile_endpoint: {str(e)}")
        return APIResponse(
            success=False, 
            message=f"Error deleting profile: {str(e)}", 
            data=None
        ) 