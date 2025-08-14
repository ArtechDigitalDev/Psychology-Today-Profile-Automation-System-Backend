"""
router.py
Defines the main API router for the application with /api prefix.
"""
from fastapi import APIRouter

# Main API router with /api prefix
router = APIRouter(prefix="/api")

# Import and include sub-routers
from app.api import  auth, profile, automation, update_logs
router.include_router(auth.router)
router.include_router(profile.router)
router.include_router(automation.router)
router.include_router(update_logs.router) 