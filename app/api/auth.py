"""
auth.py
FastAPI router for authentication endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.user import User
from app.schemas.auth import UserLogin, Token, UserOut, UserCreate
from app.auth.jwt_handler import create_access_token
from app.auth.dependencies import get_current_user
from app.schemas.response import APIResponse
from app.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/token", response_model=APIResponse)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """User login endpoint that returns JWT access token (form data)."""
    # Authenticate user
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not user.verify_password(form_data.password):
        return APIResponse(success=False, message="Incorrect username or password", data=None)
    
    # Create access token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return APIResponse(success=True, message="Login successful.", data={"access_token": access_token, "token_type": "bearer"})

@router.post("/login", response_model=APIResponse)
def login_with_json(user_data: UserLogin, db: Session = Depends(get_db)):
    """User login endpoint that returns JWT access token (JSON data)."""
    # Authenticate user
    user = db.query(User).filter(User.username == user_data.username).first()
    if not user or not user.verify_password(user_data.password):
        return APIResponse(success=False, message="Incorrect username or password", data=None)
    
    # Create access token
    access_token_expires = int(settings.JWT_ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(data={"sub": user.username},expires_delta=access_token_expires)
    
    return APIResponse(
        success=True, 
        message="Login successful.", 
        data={
            "access_token": access_token, 
            "token_type": "bearer", 
            "user": {"user_id": user.user_id, "username": user.username}
        }
    )

@router.post("/register", response_model=APIResponse, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Create a new user (for admin use)."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        return APIResponse(success=False, message="Username already registered", data=None)
    
    # Create new user
    hashed_password = User.get_password_hash(user_data.password)
    db_user = User(username=user_data.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return APIResponse(
        success=True, 
        message="User registered successfully.", 
        data={
            "user_id": db_user.user_id, 
            "username": db_user.username
        }
    )

@router.get("/me", response_model=APIResponse)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return APIResponse(
        success=True, 
        message="Current user fetched successfully.", 
        data={
            "user_id": current_user.user_id, 
            "username": current_user.username
        }
    ) 