"""
email_service.py
Email service for sending notifications via SMTP.
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Email service for sending notifications via SMTP."""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.sender_email = settings.SENDER_EMAIL
        self.sender_name = settings.SENDER_NAME
        
    def _create_message(self, to_email: str, subject: str, html_content: str, 
                       plain_text: str = None) -> MIMEMultipart:
        """Create a multipart email message."""
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{self.sender_name} <{self.sender_email}>"
        message["To"] = to_email
        
        # Add plain text version
        if plain_text:
            text_part = MIMEText(plain_text, "plain")
            message.attach(text_part)
        
        # Add HTML version
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        return message
    
    def _send_email(self, message: MIMEMultipart) -> bool:
        """Send email via SMTP."""
        try:
            # Create secure SSL/TLS context
            context = ssl.create_default_context()
            
            # Connect to SMTP server
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context) as server:
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(message)
                
            logger.info(f"Email sent successfully to {message['To']}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed. Check username and password.")
            return False
        except smtplib.SMTPRecipientsRefused:
            logger.error(f"Recipient email address refused: {message['To']}")
            return False
        except smtplib.SMTPServerDisconnected:
            logger.error("SMTP server disconnected unexpectedly.")
            return False
        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False
    
    def send_failure_notification(self, to_email: str, profile_username: str, 
                                 error_message: str, profile_id: int) -> bool:
        """Send failure notification email."""
        subject = f"Profile Automation Failed - {profile_username}"
        
        html_content = self._get_failure_template(
            profile_username=profile_username,
            error_message=error_message,
            profile_id=profile_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        plain_text = self._get_failure_template_plain(
            profile_username=profile_username,
            error_message=error_message,
            profile_id=profile_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        message = self._create_message(to_email, subject, html_content, plain_text)
        return self._send_email(message)
    
    def send_nochange_notification(self, to_email: str, profile_username: str, 
                                  profile_id: int, duration_ms: int) -> bool:
        """Send no-change notification email."""
        subject = f"Profile Automation Completed - No Changes Needed - {profile_username}"
        
        html_content = self._get_nochange_template(
            profile_username=profile_username,
            profile_id=profile_id,
            duration_ms=duration_ms,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        plain_text = self._get_nochange_template_plain(
            profile_username=profile_username,
            profile_id=profile_id,
            duration_ms=duration_ms,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        message = self._create_message(to_email, subject, html_content, plain_text)
        return self._send_email(message)
    
    def send_success_notification(self, to_email: str, profile_username: str, 
                                 profile_id: int, updated_fields: List[str], 
                                 duration_ms: int) -> bool:
        """Send success notification email."""
        subject = f"Profile Automation Completed Successfully - {profile_username}"
        
        html_content = self._get_success_template(
            profile_username=profile_username,
            profile_id=profile_id,
            updated_fields=updated_fields,
            duration_ms=duration_ms,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        plain_text = self._get_success_template_plain(
            profile_username=profile_username,
            profile_id=profile_id,
            updated_fields=updated_fields,
            duration_ms=duration_ms,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        message = self._create_message(to_email, subject, html_content, plain_text)
        return self._send_email(message)
    
    def send_summary_notification(self, to_email: str, summary_data: Dict[str, Any]) -> bool:
        """Send maintenance summary notification email."""
        subject = f"Profile Automation Summary - {summary_data.get('date', 'Unknown Date')}"
        
        html_content = self._get_summary_template(summary_data)
        plain_text = self._get_summary_template_plain(summary_data)
        
        message = self._create_message(to_email, subject, html_content, plain_text)
        return self._send_email(message)
    
    def _get_failure_template(self, profile_username: str, error_message: str, 
                             profile_id: int, timestamp: str) -> str:
        """Get HTML template for failure notification."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #dc3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .error-box {{ background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⚠️ Profile Automation Failed</h1>
                </div>
                <div class="content">
                    <h2>Profile : {profile_username}</h2>
                    <p>The automated maintenance for your Psychology Today profile has failed.</p>
                    
                    <div class="error-box">
                        <strong>Error Details:</strong><br>
                        {error_message}
                    </div>
                    
                    <p><strong>Profile ID:</strong> {profile_id}</p>
                    <p><strong>Timestamp:</strong> {timestamp}</p>
                    
                    <p>Please check your profile settings and credentials. The system will retry automatically during the next maintenance cycle.</p>
                    
                    
                </div>
                <div class="footer">
                    <p>This is an automated notification from your Profile Automation System.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_failure_template_plain(self, profile_username: str, error_message: str, 
                                   profile_id: int, timestamp: str) -> str:
        """Get plain text template for failure notification."""
        return f"""
Profile Automation Failed

Profile: {profile_username}
Profile ID: {profile_id}
Timestamp: {timestamp}

The automated maintenance for your Psychology Today profile has failed.

Error Details:
{error_message}

Please check your profile settings and credentials. The system will retry automatically during the next maintenance cycle.

This is an automated notification from your Profile Automation System.
        """
    
    def _get_nochange_template(self, profile_username: str, profile_id: int, 
                              duration_ms: int, timestamp: str) -> str:
        """Get HTML template for no-change notification."""
        duration_seconds = duration_ms / 1000
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .info-box {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Profile Automation Completed</h1>
                </div>
                <div class="content">
                    <h2>Profile: {profile_username}</h2>
                    <p>The automated maintenance for your Psychology Today profile has been completed successfully.</p>
                    
                    <div class="info-box">
                        <strong>Status:</strong> No changes needed<br>
                        <strong>Duration:</strong> {duration_seconds:.1f} seconds<br>
                        <strong>Profile ID:</strong> {profile_id}<br>
                        <strong>Timestamp:</strong> {timestamp}
                    </div>
                    
                    <p>Your profile content is already optimal and no updates were necessary. This is a good sign that your profile is well-maintained!</p>
                    
                    <p style="text-align: center;">
                        <a href="#" class="button">View Profile</a>
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from your Profile Automation System.</p>
                    <p>If you have any questions, please contact support.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_nochange_template_plain(self, profile_username: str, profile_id: int, 
                                    duration_ms: int, timestamp: str) -> str:
        """Get plain text template for no-change notification."""
        duration_seconds = duration_ms / 1000
        return f"""
Profile Automation Completed - No Changes Needed

Profile: {profile_username}
Profile ID: {profile_id}
Timestamp: {timestamp}
Duration: {duration_seconds:.1f} seconds

The automated maintenance for your Psychology Today profile has been completed successfully.

Status: No changes needed

Your profile content is already optimal and no updates were necessary. This is a good sign that your profile is well-maintained!

This is an automated notification from your Profile Automation System.
        """
    
    def _get_success_template(self, profile_username: str, profile_id: int, 
                             updated_fields: List[str], duration_ms: int, timestamp: str) -> str:
        """Get HTML template for success notification."""
        duration_seconds = duration_ms / 1000
        fields_list = "<br>".join([f"• {field}" for field in updated_fields])
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #28a745; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .success-box {{ background-color: #d4edda; border: 1px solid #c3e6cb; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
                .button {{ display: inline-block; padding: 10px 20px; background-color: #007bff; color: white; text-decoration: none; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Profile Automation Completed Successfully</h1>
                </div>
                <div class="content">
                    <h2>Profile: {profile_username}</h2>
                    <p>The automated maintenance for your Psychology Today profile has been completed successfully.</p>
                    
                    <div class="success-box">
                        <strong>Status:</strong> Successfully updated<br>
                        <strong>Duration:</strong> {duration_seconds:.1f} seconds<br>
                        <strong>Profile ID:</strong> {profile_id}<br>
                        <strong>Timestamp:</strong> {timestamp}
                    </div>
                    
                    <h3>Updated Fields:</h3>
                    <p>{fields_list}</p>
                    
                    <p>Your profile has been automatically updated with fresh, optimized content to improve your visibility and attract more clients.</p>
                    
                    <p style="text-align: center;">
                        <a href="#" class="button">View Profile</a>
                    </p>
                </div>
                <div class="footer">
                    <p>This is an automated notification from your Profile Automation System.</p>
                    <p>If you have any questions, please contact support.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_success_template_plain(self, profile_username: str, profile_id: int, 
                                   updated_fields: List[str], duration_ms: int, timestamp: str) -> str:
        """Get plain text template for success notification."""
        duration_seconds = duration_ms / 1000
        fields_list = "\n".join([f"• {field}" for field in updated_fields])
        
        return f"""
Profile Automation Completed Successfully

Profile: {profile_username}
Profile ID: {profile_id}
Timestamp: {timestamp}
Duration: {duration_seconds:.1f} seconds

The automated maintenance for your Psychology Today profile has been completed successfully.

Status: Successfully updated

Updated Fields:
{fields_list}

Your profile has been automatically updated with fresh, optimized content to improve your visibility and attract more clients.

This is an automated notification from your Profile Automation System.
        """
    
    def _get_summary_template(self, summary_data: Dict[str, Any]) -> str:
        """Get HTML template for summary notification."""
        date = summary_data.get('date', 'Unknown Date')
        total_profiles = summary_data.get('total_profiles', 0)
        success_count = summary_data.get('success_count', 0)
        failure_count = summary_data.get('failure_count', 0)
        nochange_count = summary_data.get('nochange_count', 0)
        total_duration = summary_data.get('total_duration', 0)
        period = summary_data.get('period', 'Maintenance Cycle')
        
        # Calculate success rate safely
        success_rate = 0
        if total_profiles > 0:
            success_rate = (success_count / total_profiles) * 100
        
        # Format duration nicely
        if total_duration < 60:
            duration_text = f"{total_duration:.1f} seconds"
        else:
            minutes = int(total_duration // 60)
            seconds = total_duration % 60
            duration_text = f"{minutes}m {seconds:.1f}s"
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f8f9fa; }}
                .stats {{ width: 100%; margin: 20px 0; text-align: center; }}
                .stat-box {{ display: inline-block; text-align: center; padding: 15px 10px; background-color: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin: 8px; width: 200px; min-width: 150px; vertical-align: top; }}
                .stat-number {{ font-size: 24px; font-weight: bold; }}
                .success {{ color: #28a745; }}
                .failure {{ color: #dc3545; }}
                .nochange {{ color: #ffc107; }}
                .total {{ color: #007bff; }}
                .summary-box {{ background-color: white; padding: 15px; margin: 15px 0; border-radius: 5px; border-left: 4px solid #007bff; }}
                .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Profile Automation Summary</h1>
                    <p>{date}</p>
                    <p style="font-size: 14px; opacity: 0.9;">{period}</p>
                </div>
                <div class="content">
                    <h2>Maintenance Summary</h2>
                    
                    <div class="stats">
                        <div class="stat-box">
                            <div class="stat-number total">{total_profiles}</div>
                            <div>Total Profiles</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number success">{success_count}</div>
                            <div>Success</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number failure">{failure_count}</div>
                            <div>Failed</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-number nochange">{nochange_count}</div>
                            <div>No Change</div>
                        </div>
                    </div>
                    
                    <div class="summary-box">
                        <p><strong>📈 Success Rate:</strong> {success_rate:.1f}%</p>
                        <p><strong>⏱️ Total Duration:</strong> {duration_text}</p>
                        <p><strong>📅 Period:</strong> {period}</p>
                    </div>
                    
                    <p>Your profile automation system has completed its maintenance cycle. All active profiles have been processed and updated as needed.</p>
                    
                    {f'<p style="color: #dc3545;"><strong>⚠️ Note:</strong> {failure_count} profile(s) encountered issues and may need attention.</p>' if failure_count > 0 else ''}
                    {f'<p style="color: #28a745;"><strong>✅ Great!</strong> {success_count} profile(s) were successfully updated with fresh content.</p>' if success_count > 0 else ''}
                    {f'<p style="color: #ffc107;"><strong>ℹ️ Info:</strong> {nochange_count} profile(s) were already optimal and did not need updates.</p>' if nochange_count > 0 else ''}
                </div>
                <div class="footer">
                    <p>This is an automated summary from your Profile Automation System.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _get_summary_template_plain(self, summary_data: Dict[str, Any]) -> str:
        """Get plain text template for summary notification."""
        date = summary_data.get('date', 'Unknown Date')
        total_profiles = summary_data.get('total_profiles', 0)
        success_count = summary_data.get('success_count', 0)
        failure_count = summary_data.get('failure_count', 0)
        nochange_count = summary_data.get('nochange_count', 0)
        total_duration = summary_data.get('total_duration', 0)
        period = summary_data.get('period', 'Maintenance Cycle')
        
        # Calculate success rate safely
        success_rate = 0
        if total_profiles > 0:
            success_rate = (success_count / total_profiles) * 100
        
        # Format duration nicely
        if total_duration < 60:
            duration_text = f"{total_duration:.1f} seconds"
        else:
            minutes = int(total_duration // 60)
            seconds = total_duration % 60
            duration_text = f"{minutes}m {seconds:.1f}s"
        
        return f"""
Profile Automation Summary - {date}
Period: {period}

Maintenance Summary:
• Total Profiles: {total_profiles}
• Success: {success_count}
• Failed: {failure_count}
• No Change: {nochange_count}
• Total Duration: {duration_text}
• Success Rate: {success_rate:.1f}%

Your profile automation system has completed its maintenance cycle. All active profiles have been processed and updated as needed.

{f'Note: {failure_count} profile(s) encountered issues and may need attention.' if failure_count > 0 else ''}
{f'Great! {success_count} profile(s) were successfully updated with fresh content.' if success_count > 0 else ''}
{f'Info: {nochange_count} profile(s) were already optimal and did not need updates.' if nochange_count > 0 else ''}

This is an automated summary from your Profile Automation System.
        """

# Global email service instance
email_service = EmailService() 