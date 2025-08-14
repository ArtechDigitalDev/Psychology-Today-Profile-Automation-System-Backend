"""
update_logs.py
FastAPI router for viewing update logs.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.auth.dependencies import get_current_user
from app.models.user import User
from app.models.update_log import UpdateLog
from app.schemas.update_log import UpdateLogOut, UpdateLogSummary
from app.schemas.response import APIResponse
from typing import Optional
from datetime import datetime, timedelta
from app.models.profile import Profile


router = APIRouter(prefix="/update-logs", tags=["Update Logs"])

# get recent logs
@router.get("/", response_model=APIResponse)
def get_recent_logs_endpoint(
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent update logs across all profiles."""
    try:
        logs = UpdateLog.get_recent_logs(db, limit=limit)
        
        # Populate pt_username for each log
        from app.models.profile import Profile
        log_data = []
        for log in logs:
            profile = db.query(Profile).filter(Profile.profile_id == log.profile_id).first()
            pt_username = profile.pt_username if profile else f"Profile_{log.profile_id}"
            
            log_dict = UpdateLogOut.model_validate(log).model_dump()
            log_dict["pt_username"] = pt_username
            log_data.append(log_dict)
        
        return APIResponse(
            success=True,
            message="Update logs retrieved successfully.",
            data=log_data
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to retrieve update logs: {str(e)}",
            data=None
        )

# get logs by profile
@router.get("/profile/{pt_username}", response_model=APIResponse)
def get_profile_logs_endpoint(
    pt_username: str,
    limit: int = Query(100, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get update logs for a specific profile by pt_username."""
    try:
        # First get the profile by pt_username
        profile = db.query(Profile).filter(Profile.pt_username == pt_username).first()
        
        if not profile:
            # Get all available pt_usernames for better error message
            all_profiles = db.query(Profile).all()
            available_usernames = [p.pt_username for p in all_profiles]
            
            error_message = f"Profile with pt_username '{pt_username}' not found."
            if available_usernames:
                error_message += f" Available profiles: {', '.join(available_usernames)}"
            else:
                error_message += " No profiles found in database."
            
            return APIResponse(
                success=False,
                message=error_message,
                data=None
            )
        
        logs = UpdateLog.get_profile_logs(db, profile_id=profile.profile_id, limit=limit)
        
        # Populate pt_username for each log
        log_data = []
        for log in logs:
            log_dict = UpdateLogOut.model_validate(log).model_dump()
            log_dict["pt_username"] = pt_username  # Use the pt_username from URL
            log_data.append(log_dict)
        
        return APIResponse(
            success=True,
            message=f"Update logs for profile '{pt_username}' retrieved successfully.",
            data=log_data
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to retrieve profile logs: {str(e)}",
            data=None
        )

# get logs by outcome
@router.get("/outcome/{outcome}", response_model=APIResponse)
def get_logs_by_outcome_endpoint(
    outcome: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get update logs filtered by outcome (Success, Failure, Warning)."""
    try:
        if outcome not in ["Success", "Failure", "NoChange", "Warning"]:
            return APIResponse(
                success=False,
                message="Invalid outcome. Must be 'Success', 'Failure', 'NoChange', or 'Warning'.",
                data=None
            )
        
        logs = UpdateLog.get_logs_by_outcome(db, outcome=outcome, limit=limit)
        
        # Populate pt_username for each log
        from app.models.profile import Profile
        log_data = []
        for log in logs:
            profile = db.query(Profile).filter(Profile.profile_id == log.profile_id).first()
            pt_username = profile.pt_username if profile else f"Profile_{log.profile_id}"
            
            log_dict = UpdateLogOut.model_validate(log).model_dump()
            log_dict["pt_username"] = pt_username
            log_data.append(log_dict)
        
        return APIResponse(
            success=True,
            message=f"Update logs with outcome '{outcome}' retrieved successfully.",
            data=log_data
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to retrieve logs by outcome: {str(e)}",
            data=None
        )

# get logs summary
@router.get("/summary", response_model=APIResponse)
def get_logs_summary_endpoint(
    days: int = Query(7, ge=1, le=365),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get summary statistics of update logs for the last N days."""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        logs = UpdateLog.get_logs_by_date_range(db, start_date, end_date)
        
        # Calculate statistics
        total_logs = len(logs)
        success_count = len([log for log in logs if log.outcome == "Success"])
        failure_count = len([log for log in logs if log.outcome == "Failure"])
        nochange_count = len([log for log in logs if log.outcome == "NoChange"])
        warning_count = len([log for log in logs if log.outcome == "Warning"])
        
        # Calculate average duration
        durations = [log.duration_ms for log in logs if log.duration_ms is not None]
        average_duration_ms = sum(durations) / len(durations) if durations else None
        
        # Get recent logs (last 10) with pt_username
        recent_logs = logs[:10]
        
        # Populate pt_username for recent logs
        from app.models.profile import Profile
        recent_logs_data = []
        for log in recent_logs:
            profile = db.query(Profile).filter(Profile.profile_id == log.profile_id).first()
            pt_username = profile.pt_username if profile else f"Profile_{log.profile_id}"
            
            log_dict = UpdateLogOut.model_validate(log).model_dump()
            log_dict["pt_username"] = pt_username
            recent_logs_data.append(log_dict)
        
        summary = UpdateLogSummary(
            total_logs=total_logs,
            success_count=success_count,
            failure_count=failure_count,
            nochange_count=nochange_count,
            warning_count=warning_count,
            average_duration_ms=average_duration_ms,
            recent_logs=recent_logs_data
        )
        
        return APIResponse(
            success=True,
            message=f"Update logs summary for last {days} days retrieved successfully.",
            data=summary
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to retrieve logs summary: {str(e)}",
            data=None
        )

# get logs stats
@router.get("/stats", response_model=APIResponse)
def get_logs_stats_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get overall statistics of update logs."""
    try:
        # Get all logs
        all_logs = UpdateLog.get_recent_logs(db, limit=10000)  # Large limit to get all
        
        # Calculate overall statistics
        total_logs = len(all_logs)
        success_count = len([log for log in all_logs if log.outcome == "Success"])
        failure_count = len([log for log in all_logs if log.outcome == "Failure"])
        nochange_count = len([log for log in all_logs if log.outcome == "NoChange"])
        warning_count = len([log for log in all_logs if log.outcome == "Warning"])
        
        # Calculate success rate
        success_rate = (success_count / total_logs * 100) if total_logs > 0 else 0
        
        # Calculate average duration
        durations = [log.duration_ms for log in all_logs if log.duration_ms is not None]
        average_duration_ms = sum(durations) / len(durations) if durations else None
        
        # Get logs by profile with pt_username
        profile_stats = {}
        for log in all_logs:
            profile_id = log.profile_id
            
            # Get profile details if not already cached
            if profile_id not in profile_stats:
                profile = db.query(Profile).filter(Profile.profile_id == profile_id).first()
                pt_username = profile.pt_username if profile else f"Profile_{profile_id}"
                
                profile_stats[profile_id] = {
                    "pt_username": pt_username,
                    "total": 0, 
                    "success": 0, 
                    "failure": 0, 
                    "nochange": 0
                }
            
            profile_stats[profile_id]["total"] += 1
            if log.outcome == "Success":
                profile_stats[profile_id]["success"] += 1
            elif log.outcome == "Failure":
                profile_stats[profile_id]["failure"] += 1
            elif log.outcome == "NoChange":
                profile_stats[profile_id]["nochange"] += 1
        stats = {
            "total_logs": total_logs,
            "success_count": success_count,
            "failure_count": failure_count,
            "nochange_count": nochange_count,
            "warning_count": warning_count,
            "success_rate_percentage": round(success_rate, 2),
            "average_duration_ms": round(average_duration_ms, 2) if average_duration_ms else None,
            "profile_stats": profile_stats
        }
        
        return APIResponse(
            success=True,
            message="Update logs statistics retrieved successfully.",
            data=stats
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to retrieve logs statistics: {str(e)}",
            data=None
        )

# get weekly logs stats
@router.get("/stats/weekly", response_model=APIResponse)
def get_weekly_logs_stats_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly statistics of update logs (last 7 days)."""
    try:
        # Calculate date range for the last 7 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        # Get logs for the last 7 days
        weekly_logs = UpdateLog.get_logs_by_date_range(db, start_date, end_date)
        
        # Calculate weekly statistics
        total_logs = len(weekly_logs)
        success_count = len([log for log in weekly_logs if log.outcome == "Success"])
        failure_count = len([log for log in weekly_logs if log.outcome == "Failure"])
        nochange_count = len([log for log in weekly_logs if log.outcome == "NoChange"])
        warning_count = len([log for log in weekly_logs if log.outcome == "Warning"])
        
        # Calculate success rate
        success_rate = (success_count / total_logs * 100) if total_logs > 0 else 0
        
        # Calculate average duration
        durations = [log.duration_ms for log in weekly_logs if log.duration_ms is not None]
        average_duration_ms = sum(durations) / len(durations) if durations else None
        
        # Get logs by profile with pt_username
        profile_stats = {}
        for log in weekly_logs:
            profile_id = log.profile_id
            
            # Get profile details if not already cached
            if profile_id not in profile_stats:
                profile = db.query(Profile).filter(Profile.profile_id == profile_id).first()
                pt_username = profile.pt_username if profile else f"Profile_{profile_id}"
                
                profile_stats[profile_id] = {
                    "pt_username": pt_username,
                    "total": 0, 
                    "success": 0, 
                    "failure": 0, 
                    "nochange": 0,
                    "warning": 0
                }
            
            profile_stats[profile_id]["total"] += 1
            if log.outcome == "Success":
                profile_stats[profile_id]["success"] += 1
            elif log.outcome == "Failure":
                profile_stats[profile_id]["failure"] += 1
            elif log.outcome == "NoChange":
                profile_stats[profile_id]["nochange"] += 1
            elif log.outcome == "Warning":
                profile_stats[profile_id]["warning"] += 1
        
        # Calculate daily breakdown for the week
        daily_stats = {}
        for i in range(7):
            date = end_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            day_logs = [log for log in weekly_logs if log.executed_at.date() == date.date()]
            
            daily_stats[date_str] = {
                "total": len(day_logs),
                "success": len([log for log in day_logs if log.outcome == "Success"]),
                "failure": len([log for log in day_logs if log.outcome == "Failure"]),
                "nochange": len([log for log in day_logs if log.outcome == "NoChange"]),
                "warning": len([log for log in day_logs if log.outcome == "Warning"])
            }
        
        stats = {
            "period": "last_7_days",
            "start_date": start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "total_logs": total_logs,
            "success_count": success_count,
            "failure_count": failure_count,
            "nochange_count": nochange_count,
            "warning_count": warning_count,
            "success_rate_percentage": round(success_rate, 2),
            "average_duration_ms": round(average_duration_ms, 2) if average_duration_ms else None,
            "profile_stats": profile_stats,
            "daily_breakdown": daily_stats
        }
        
        return APIResponse(
            success=True,
            message="Weekly update logs statistics retrieved successfully.",
            data=stats
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message=f"Failed to retrieve weekly logs statistics: {str(e)}",
            data=None
        ) 