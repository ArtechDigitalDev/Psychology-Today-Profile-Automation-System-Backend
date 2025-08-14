# Email Service (SMTP) Implementation Guide

## Overview

The Profile Automation System now includes a comprehensive email notification service that sends automated emails for different maintenance outcomes. The service uses SMTP to send professional, HTML-formatted emails with both HTML and plain text versions.

## Features

### 1. **Failure Email Notifications Only**

#### **Failure Notifications**
- Sent when profile maintenance fails
- Includes error details and troubleshooting suggestions
- Red header with warning icon
- Professional error message formatting
- Sent to admin email address only

### 2. **Email Templates**

#### **HTML Templates**
- Responsive design (max-width: 600px)
- Professional color scheme
- Icons and visual indicators
- Call-to-action buttons
- Mobile-friendly layout

#### **Plain Text Templates**
- Fallback for email clients that don't support HTML
- Clean, readable format
- All essential information included
- No formatting dependencies

### 3. **SMTP Integration**

#### **Secure Connection**
- SSL/TLS encryption
- SMTP_SSL for secure communication
- Proper error handling for connection issues

#### **Authentication**
- Username/password authentication
- Support for app passwords (Gmail)
- Secure credential storage in environment variables

## Configuration

### 1. **Environment Variables**

Add these to your `.env` file:

```env
# SMTP Settings
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SENDER_EMAIL=your_email@gmail.com
SENDER_NAME=Profile Automation System
ADMIN_EMAIL=admin@example.com
```

### 2. **Gmail Setup (Recommended)**

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate an App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
   - Use this password in `SMTP_PASSWORD`

3. **Alternative: Less Secure Apps** (not recommended)
   - Enable "Less secure app access" in Gmail settings
   - Use your regular password

### 3. **Other SMTP Providers**

#### **Outlook/Hotmail**
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
```

#### **Yahoo**
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
```

#### **Custom SMTP Server**
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
```

## Database Schema

### No Profile Model Changes Required

The Profile model remains unchanged. No additional fields are needed.

### Usage

```python
# Failure emails are sent to the admin email address configured in .env
# No profile-specific email addresses are needed
```

## Integration with Maintenance System

### 1. **Automatic Email Sending**

The email service is automatically integrated into the maintenance process:

- **Failure**: Email sent to admin when maintenance fails
- **Success**: No email sent (as requested)
- **No-Change**: No email sent (as requested)
- **Summary**: No email sent (as requested)

### 2. **Error Handling**

- Email failures don't stop maintenance process
- All email errors are logged
- Graceful fallback if email service unavailable

### 3. **Performance**

- Emails sent asynchronously
- No impact on maintenance speed
- Efficient SMTP connection handling

## Email Templates

### 1. **Failure Template**
- Red header with warning icon
- Error details in highlighted box
- Profile information and timestamp
- Troubleshooting suggestions
- Sent to admin email address

## Testing

### 1. **Test Script**

Run the test script to verify email functionality:

```bash
python test_email_service.py
```

### 2. **Manual Testing**

```python
from app.services.email_service import email_service

# Test failure notification (only type used)
email_service.send_failure_notification(
    to_email="admin@example.com",
    profile_username="test_user",
    error_message="Login failed",
    profile_id=1
)
```

### 3. **Configuration Testing**

1. Update `.env` with your SMTP settings
2. Run test script
3. Check email delivery
4. Verify HTML and plain text versions

## Troubleshooting

### 1. **Common SMTP Errors**

#### **Authentication Failed**
- Check username and password
- Verify app password for Gmail
- Ensure 2FA is enabled

#### **Connection Refused**
- Check SMTP server and port
- Verify firewall settings
- Test with different port (587 vs 465)

#### **Recipient Refused**
- Check email address format
- Verify recipient email exists
- Check spam folder

### 2. **Gmail Specific Issues**

#### **App Password Required**
- Enable 2-Factor Authentication
- Generate app password
- Use app password instead of regular password

#### **Less Secure Apps**
- Enable "Less secure app access"
- Use regular password
- Note: Less secure than app passwords

### 3. **Email Delivery Issues**

#### **Not Receiving Emails**
- Check spam/junk folder
- Verify sender email is correct
- Check email client settings

#### **HTML Not Displaying**
- Check email client HTML support
- Plain text version is always included
- Test with different email clients

## Security Considerations

### 1. **Credential Security**
- Store SMTP credentials in environment variables
- Never commit credentials to version control
- Use app passwords instead of regular passwords

### 2. **Email Content**
- No sensitive information in email content
- Profile passwords are never included
- Error messages are sanitized

### 3. **Rate Limiting**
- Emails sent only when needed
- No spam or bulk email functionality
- Respectful of SMTP server limits

## Future Enhancements

### 1. **Template Customization**
- User-configurable email templates
- Custom branding options
- Multiple language support

### 2. **Advanced Notifications**
- SMS notifications
- Slack/Discord integration
- Webhook notifications

### 3. **Email Preferences**
- User preference settings
- Frequency controls
- Notification type selection

## Support

For issues with the email service:

1. Check the troubleshooting section
2. Verify SMTP configuration
3. Test with the provided test script
4. Check application logs for error details
5. Contact support with specific error messages 