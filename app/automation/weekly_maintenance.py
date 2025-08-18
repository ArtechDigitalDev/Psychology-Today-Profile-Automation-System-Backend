"""
weekly_maintenance.py
Weekly automated maintenance for Psychology Today profiles.
"""
import asyncio
import schedule
import time
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.models.profile import Profile
from app.models.update_log import UpdateLog
from app.automation.playwright_automation import login_and_edit_profile
from app.services.email_service import email_service
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeeklyMaintenanceScheduler:
    """Scheduler for weekly profile maintenance automation."""
    
    def __init__(self):
        self.is_running = False
        self.is_task_running = False  # Track if maintenance task is currently running
        self.last_task_start = None  # Track when the last task started
        self.should_stop = False  # Flag to stop maintenance immediately
        self.db = next(get_db())
    
    def get_active_profiles(self) -> List[Profile]:
        """Get all active profiles that need maintenance."""
        return self.db.query(Profile).filter(
            Profile.is_active == True
        ).all()
    
    def update_profile_status(self, profile: Profile, status: str, success: bool = True):
        """Update profile status and timestamps."""
        profile.status = status
        profile.last_run_at = datetime.now(timezone.utc)
        
        if success:
            profile.last_success_at = datetime.now(timezone.utc)
            profile.next_run_at = datetime.now(timezone.utc) + timedelta(days=7)
        
        self.db.commit()
        logger.info(f"Profile {profile.pt_username} status updated to: {status}")
    
    def process_single_profile(self, profile: Profile) -> bool:
        start_time = time.time()
        
        # Check if should stop before processing this profile
        if self.should_stop:
            logger.info(f"Stop signal received. Skipping profile: {profile.pt_username}")
            return False
            
        try:
            logger.info(f"Starting maintenance for profile: {profile.pt_username}")
            self.update_profile_status(profile, "Running", False)
            password = profile.get_password()
            
            # Run automation and get updated fields
            updated_fields = self.run_profile_automation(profile, password)
            duration_ms = int((time.time() - start_time) * 1000)
            
            logger.info(f"Automation completed for {profile.pt_username}. Updated fields: {updated_fields}")
            
            # Determine outcome based on updated_fields
            if updated_fields and len(updated_fields) > 0:
                # Success: Fields were updated
                self.update_profile_status(profile, "Completed", True)
                UpdateLog.create_log(
                    db=self.db,
                    profile_id=profile.profile_id,
                    outcome="Success",
                    duration_ms=duration_ms,
                    fields_edited=updated_fields,
                    log_details=f"Profile {profile.pt_username} maintenance completed successfully! Updated fields: {', '.join(list(updated_fields.keys()))}"
                )
                logger.info(f"Profile {profile.pt_username} maintenance completed successfully. Fields updated: {list(updated_fields.keys())}")
                
                # No email notification for success (as requested)
                pass
                
                return "success"
            else:
                # NoChange: No fields were updated (this is normal)
                self.update_profile_status(profile, "NoChange", True)
                UpdateLog.create_log(
                    db=self.db,
                    profile_id=profile.profile_id,
                    outcome="NoChange",
                    duration_ms=duration_ms,
                    fields_edited={},
                    log_details=f"Profile {profile.pt_username} maintenance completed! No updates needed (content already optimal)"
                )
                logger.info(f"Profile {profile.pt_username} maintenance completed. No fields were updated (content already optimal).")
                
                # No email notification for no-change (as requested)
                pass
                
                return "nochange"
                
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Determine specific error type for better logging
            error_type = "Unknown"
            if "LoginError" in str(type(e)) or "Invalid credentials" in str(e) or "Login failed" in str(e):
                error_type = "Login"
            elif "NavigationError" in str(type(e)) or "timeout" in str(e).lower():
                error_type = "Navigation"
            elif "ElementNotFoundError" in str(type(e)):
                error_type = "ElementNotFound"
            elif "ContentGenerationError" in str(type(e)):
                error_type = "ContentGeneration"
            elif "ProfileUpdateError" in str(type(e)):
                error_type = "ProfileUpdate"
            elif "NetworkError" in str(type(e)):
                error_type = "Network"
            
            # Create more user-friendly error messages
            if error_type == "Login":
                if "Invalid credentials" in str(e) or "wrong username" in str(e).lower():
                    error_message = f"Login failed for profile {profile.pt_username}: Invalid username or password"
                elif "still on login page" in str(e).lower():
                    error_message = f"Login failed for profile {profile.pt_username}: Could not access account (check credentials)"
                elif "account locked" in str(e).lower():
                    error_message = f"Login failed for profile {profile.pt_username}: Account is locked or suspended"
                elif "too many attempts" in str(e).lower():
                    error_message = f"Login failed for profile {profile.pt_username}: Too many failed login attempts"
                elif "captcha" in str(e).lower():
                    error_message = f"Login failed for profile {profile.pt_username}: CAPTCHA verification required"
                else:
                    error_message = f"Login failed for profile {profile.pt_username}: {str(e)}"
            elif error_type == "Navigation":
                error_message = f"Navigation error for profile {profile.pt_username}: Could not load required pages"
            elif error_type == "ElementNotFound":
                error_message = f"Website structure changed for profile {profile.pt_username}: Required elements not found"
            elif error_type == "ContentGeneration":
                error_message = f"AI content generation failed for profile {profile.pt_username}: {str(e)}"
            elif error_type == "ProfileUpdate":
                error_message = f"Profile update failed for profile {profile.pt_username}: Could not save changes"
            elif error_type == "Network":
                error_message = f"Network error for profile {profile.pt_username}: Connection issues detected"
            else:
                error_message = f"Unexpected error for profile {profile.pt_username}: {str(e)}"
            self.update_profile_status(profile, "Error", False)
            
            UpdateLog.create_log(
                db=self.db,
                profile_id=profile.profile_id,
                outcome="Failure",
                duration_ms=duration_ms,
                log_details=error_message
            )
            logger.error(error_message)
            
            # Send failure email notification to admin
            try:
                from app.config import settings
                admin_email = getattr(settings, 'ADMIN_EMAIL', None)
                if admin_email:
                    email_service.send_failure_notification(
                        to_email=admin_email,
                        profile_username=profile.pt_username,
                        error_message=error_message,
                        profile_id=profile.profile_id
                    )
                    logger.info(f"Failure notification email sent to admin: {admin_email}")
            except Exception as email_error:
                logger.error(f"Failed to send failure notification email: {str(email_error)}")
            
            return "failure"

    def send_summary_notification(self, total_profiles: int, success_count: int, 
                                 failure_count: int, nochange_count: int, total_duration: float):
        """Send summary email notification after maintenance completion."""
        try:
            from app.config import settings
            admin_email = getattr(settings, 'ADMIN_EMAIL', None)
            
            if not admin_email:
                logger.warning("No admin email configured. Skipping summary notification.")
                return
            
            # Prepare summary data
            summary_data = {
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_profiles': total_profiles,
                'success_count': success_count,
                'failure_count': failure_count,
                'nochange_count': nochange_count,
                'total_duration': total_duration
            }
            
            # Send summary email
            success = email_service.send_summary_notification(
                to_email=admin_email,
                summary_data=summary_data
            )
            
            if success:
                logger.info(f"Summary notification email sent successfully to admin: {admin_email}")
            else:
                logger.error(f"Failed to send summary notification email to admin: {admin_email}")
                
        except Exception as e:
            logger.error(f"Error sending summary notification: {str(e)}")

    def run_profile_automation(self, profile: Profile, password: str) -> dict:
        max_retries = 3
        for attempt in range(max_retries):
            try:
                logger.info(f"Starting automation for {profile.pt_username} (attempt {attempt + 1}/{max_retries})")
                # Call the automation function, get updated fields
                updated_fields = login_and_edit_profile(profile.pt_username, password)
                logger.info(f"Automation completed for {profile.pt_username}. Updated fields: {updated_fields}")
                
                # Check if any fields were actually updated
                if updated_fields and len(updated_fields) > 0:
                    logger.info(f"Fields updated for {profile.pt_username}: {list(updated_fields.keys())}")
                    return updated_fields
                else:
                    logger.info(f"No fields were updated for {profile.pt_username} - this is normal if content is already optimal")
                    return {}  # Empty dict means NoChange
                    
            except Exception as e:
                logger.error(f"Automation failed for {profile.pt_username} (attempt {attempt + 1}/{max_retries}): {str(e)}")
                logger.error(f"Exception details: {type(e).__name__}: {e}")
                
                # Unified retry logic for ALL error types
                if "LoginError" in str(type(e)) or "Invalid credentials" in str(e) or "Login failed" in str(e):
                    logger.error(f"Login error for {profile.pt_username} - will retry")
                    logger.error(f"Login error details: {str(e)}")
                elif "NavigationError" in str(type(e)) or "timeout" in str(e).lower():
                    logger.error(f"Navigation/timeout error for {profile.pt_username}")
                elif "ElementNotFoundError" in str(type(e)):
                    logger.error(f"Element not found error for {profile.pt_username} - website structure may have changed")
                elif "ContentGenerationError" in str(type(e)):
                    logger.error(f"Content generation error for {profile.pt_username}")
                else:
                    logger.error(f"Generic error for {profile.pt_username}")
                
                # Retry logic for ALL error types
                if attempt < max_retries - 1:
                    # Calculate wait time based on error type
                    if "NavigationError" in str(type(e)) or "timeout" in str(e).lower():
                        wait_time = (attempt + 1) * 60  # Longer wait for network issues
                    else:
                        wait_time = (attempt + 1) * 30  # Standard wait for other errors
                    
                    logger.info(f"Retrying in {wait_time} seconds... (attempt {attempt + 2}/{max_retries})")
                    
                    # Check for stop signal during retry wait
                    for _ in range(wait_time):
                        if self.should_stop:
                            logger.info(f"Stop signal received during retry wait for {profile.pt_username}. Stopping.")
                            raise Exception("Maintenance stopped by user")
                        time.sleep(1)
                else:
                    # Final attempt failed - re-raise the exception to be caught by outer function
                    import traceback
                    logger.error(f"Final attempt failed after {max_retries} attempts. Full traceback: {traceback.format_exc()}")
                    # Re-raise the original exception to preserve error details
                    raise e
    
    def run_weekly_maintenance(self):
        """Run maintenance for all active profiles."""
        # Check if task is already running
        if self.is_task_running:
            logger.warning("Weekly maintenance is already running, skipping this cycle")
            return
        
        self.is_task_running = True
        self.should_stop = False  # Reset stop flag
        self.last_task_start = datetime.now(timezone.utc)
        
        try:
            logger.info("Starting weekly maintenance cycle")
            
            profiles = self.get_active_profiles()
            logger.info(f"Found {len(profiles)} active profiles to process")
            
            success_count = 0
            error_count = 0
            nochange_count = 0
            
            for i, profile in enumerate(profiles, 1):
                # Check if should stop before processing each profile
                if self.should_stop:
                    logger.info("Stop signal received. Stopping maintenance cycle.")
                    break
                
                logger.info(f"Processing profile {i}/{len(profiles)}: {profile.pt_username}")
                result = self.process_single_profile(profile)
                if result == "success":
                    success_count += 1
                elif result == "nochange":
                    nochange_count += 1
                else:
                    error_count += 1
                
                # Check if should stop before delay
                if self.should_stop:
                    logger.info("Stop signal received. Stopping maintenance cycle.")
                    break
                
                # Add 15 second delay between profiles (except for the last one)
                if i < len(profiles):
                    logger.info(f"Waiting 15 seconds before processing next profile...")
                    # Check for stop signal every 1 second during delay
                    for _ in range(15):
                        if self.should_stop:
                            logger.info("Stop signal received during delay. Stopping maintenance cycle.")
                            break
                        time.sleep(1)
                    
                    if self.should_stop:
                        break
            
            task_duration = datetime.now(timezone.utc) - self.last_task_start
            total_duration_seconds = task_duration.total_seconds()
            
            if self.should_stop:
                logger.info(f"Weekly maintenance stopped by user. Processed: {success_count} success, {nochange_count} no-change, {error_count} errors")
            else:
                logger.info(f"Weekly maintenance completed in {task_duration}. Success: {success_count}, No-change: {nochange_count}, Errors: {error_count}")
                
                # Send summary email notification
                self.send_summary_notification(
                    total_profiles=len(profiles),
                    success_count=success_count,
                    failure_count=error_count,
                    nochange_count=nochange_count,
                    total_duration=total_duration_seconds
                )
        finally:
            self.is_task_running = False
            self.should_stop = False  # Reset stop flag
            self.last_task_start = None
    
    def start_scheduler(self):
        """Start the weekly scheduler."""
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        schedule.clear()
        
        print("Scheduler started")

        # Schedule weekly maintenance (every Sunday at 2 AM)
        schedule.every().monday.at("03:30").do(self.run_weekly_maintenance)

        
        # Also schedule for immediate testing
        # schedule.every().day.at("14:00").do(self.run_weekly_maintenance)
        # schedule.every(1).minutes.do(lambda: print("Test: ১ মিনিট হয়ে গেছে!"))

        # schedule.every(30).seconds.do(self.run_weekly_maintenance)
        
        # logger.info("Weekly maintenance scheduler started")
        # logger.info("Maintenance scheduled for every Sunday at 2:00 AM")
        
        # Run the scheduler loop
        while self.is_running:
            schedule.run_pending()
            print("seconds passed - 10")
            time.sleep(10)  # Check every 2 seconds
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        self.is_running = False
        self.should_stop = True  # Signal to stop current maintenance task
        logger.info("Weekly maintenance scheduler stopped")
    
    def stop_maintenance_immediately(self):
        """Stop the current maintenance task immediately."""
        if self.is_task_running:
            self.should_stop = True
            logger.info("Stop signal sent to current maintenance task")
        else:
            logger.info("No maintenance task is currently running")

# Global scheduler instance
scheduler = WeeklyMaintenanceScheduler()

def start_weekly_maintenance():
    """Start the weekly maintenance scheduler."""
    scheduler.start_scheduler()

def stop_weekly_maintenance():
    """Stop the weekly maintenance scheduler."""
    scheduler.stop_scheduler()

def stop_maintenance_immediately():
    """Stop the current maintenance task immediately."""
    scheduler.stop_maintenance_immediately()

def run_maintenance_now():
    """Run maintenance immediately for testing."""
    scheduler.run_weekly_maintenance()

if __name__ == "__main__":
    # For testing - run maintenance immediately
    run_maintenance_now() 