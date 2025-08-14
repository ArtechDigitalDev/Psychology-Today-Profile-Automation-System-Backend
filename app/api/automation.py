"""
automation.py
FastAPI router for automation control endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.profile import Profile
from app.models.update_log import UpdateLog
from app.schemas.response import APIResponse
from app.automation.weekly_maintenance import (
    start_weekly_maintenance, 
    stop_weekly_maintenance, 
    run_maintenance_now,
    stop_maintenance_immediately,
    scheduler
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/automation", tags=["Automation"])

@router.post("/start", response_model=APIResponse)
def start_automation_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Start the weekly maintenance automation scheduler."""
    try:
        if scheduler.is_running:
            return APIResponse(
                success=False, 
                message="Automation scheduler is already running.", 
                data=None
            )
        
        # Start the scheduler in a background thread
        import threading
        scheduler_thread = threading.Thread(target=start_weekly_maintenance, daemon=True)
        scheduler_thread.start()
        
        return APIResponse(
            success=True, 
            message="Weekly maintenance automation started successfully.", 
            data={"status": "running"}
        )
    except Exception as e:
        logger.error(f"Error starting automation: {str(e)}")
        return APIResponse(
            success=False, 
            message=f"Failed to start automation: {str(e)}", 
            data=None
        )

@router.post("/stop", response_model=APIResponse)
def stop_automation_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Stop the weekly maintenance automation scheduler and any running maintenance tasks."""
    try:
        # Stop any running maintenance task immediately
        if scheduler.is_task_running:
            stop_maintenance_immediately()
            logger.info("Stop signal sent to running maintenance task")
        
        # Stop the scheduler if it's running
        if scheduler.is_running:
            stop_weekly_maintenance()
            logger.info("Weekly maintenance scheduler stopped")
        
        return APIResponse(
            success=True, 
            message="Automation stopped successfully. Any running maintenance tasks will stop at the next safe point.", 
            data={"status": "stopped"}
        )
    except Exception as e:
        logger.error(f"Error stopping automation: {str(e)}")
        return APIResponse(
            success=False, 
            message=f"Failed to stop automation: {str(e)}", 
            data=None
        )



@router.post("/run-now", response_model=APIResponse)
def run_maintenance_now_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Run maintenance immediately for all active profiles."""
    try:
        # Check if maintenance is already running
        if scheduler.is_task_running:
            return APIResponse(
                success=False, 
                message="Maintenance is already running. Please wait for it to complete or stop it first.", 
                data={"status": "already_running"}
            )
        
        # Run maintenance in a background thread
        import threading
        maintenance_thread = threading.Thread(target=run_maintenance_now, daemon=True)
        maintenance_thread.start()
        
        return APIResponse(
            success=True, 
            message="Maintenance started immediately. Check logs for progress.", 
            data={"status": "running_now"}
        )
    except Exception as e:
        logger.error(f"Error running maintenance: {str(e)}")
        return APIResponse(
            success=False, 
            message=f"Failed to run maintenance: {str(e)}", 
            data=None
        )

@router.get("/status", response_model=APIResponse)
def get_automation_status_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the current status of automation and profiles."""
    try:
        # Get comprehensive automation status
        automation_status = {
            "scheduler_running": scheduler.is_running,
            "task_running": scheduler.is_task_running,
            "automation_active": scheduler.is_running or scheduler.is_task_running,
            "last_task_start": scheduler.last_task_start.isoformat() if scheduler.last_task_start else None,
            "should_stop": scheduler.should_stop,
            "active_profiles": 0,
            "profiles_by_status": {},
            "currently_processing": None
        }
        
        # Get profile statistics
        profiles = db.query(Profile).all()
        active_profiles = db.query(Profile).filter(Profile.is_active == True).count()
        
        automation_status["active_profiles"] = active_profiles
        
        # Count profiles by status and find currently processing profile
        status_counts = {}
        currently_processing = None
        
        for profile in profiles:
            status = profile.status or "Unknown"
            status_counts[status] = status_counts.get(status, 0) + 1
            
            # Check if any profile is currently running
            if status == "Running":
                currently_processing = {
                    "profile_id": profile.profile_id,
                    "pt_username": profile.pt_username,
                    "status": status,
                    "last_run_at": profile.last_run_at.isoformat() if profile.last_run_at else None
                }
        
        automation_status["profiles_by_status"] = status_counts
        automation_status["currently_processing"] = currently_processing
        
        # Add summary status
        if scheduler.is_task_running:
            if scheduler.should_stop:
                automation_status["summary"] = "Maintenance task is running but will stop at next safe point"
            else:
                automation_status["summary"] = "Maintenance task is currently running"
        elif scheduler.is_running:
            automation_status["summary"] = "Automation scheduler is running (waiting for next cycle)"
        else:
            automation_status["summary"] = "Automation is not running"
        
        return APIResponse(
            success=True, 
            message="Automation status retrieved successfully.", 
            data=automation_status
        )
    except Exception as e:
        logger.error(f"Error getting automation status: {str(e)}")
        return APIResponse(
            success=False, 
            message=f"Failed to get automation status: {str(e)}",
            data=None
        )

@router.get("/logs", response_model=APIResponse)
def get_automation_logs_endpoint(
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    """Get recent automation logs from database."""
    try:
        # Get recent logs from database
        logs = UpdateLog.get_recent_logs(db=next(get_db()), limit=limit)
        
        # Convert to log format
        log_entries = []
        for log in logs:
            log_entries.append({
                "timestamp": log.executed_at.isoformat(),
                "level": "INFO" if log.outcome == "Success" else "ERROR",
                "message": log.log_details or f"Profile {log.profile_id} {log.outcome.lower()}",
                "profile_id": log.profile_id,
                "duration_ms": log.duration_ms,
                "outcome": log.outcome
            })
        
        return APIResponse(
            success=True, 
            message="Automation logs retrieved successfully.", 
            data={"logs": log_entries}
        )
    except Exception as e:
        logger.error(f"Error getting automation logs: {str(e)}")
        return APIResponse(
            success=False, 
            message=f"Failed to get automation logs: {str(e)}",
            data=None
        )

@router.get("/is-running", response_model=APIResponse)
def check_automation_running_endpoint(
    current_user: User = Depends(get_current_user)
):
    """Quick check to see if automation is currently running."""
    try:
        is_running = scheduler.is_running or scheduler.is_task_running
        
        status_info = {
            "is_running": is_running,
            "scheduler_running": scheduler.is_running,
            "task_running": scheduler.is_task_running,
            "summary": "Automation is running" if is_running else "Automation is not running"
        }
        
        # Add currently processing profile if any
        if scheduler.is_task_running:
            try:
                db = next(get_db())
                running_profile = db.query(Profile).filter(Profile.status == "Running").first()
                if running_profile:
                    status_info["currently_processing"] = {
                        "pt_username": running_profile.pt_username,
                        "profile_id": running_profile.profile_id
                    }
            except Exception:
                pass  # Don't fail the main check if we can't get profile details
        
        return APIResponse(
            success=True,
            message=status_info["summary"],
            data=status_info
        )
    except Exception as e:
        logger.error(f"Error checking automation status: {str(e)}")
        return APIResponse(
            success=False,
            message=f"Failed to check automation status: {str(e)}",
            data=None
        ) 