# Psychology Today Profile Automation System Guide

## **System Overview**

This system automates weekly maintenance for Psychology Today therapist profiles using AI-generated content and browser automation. It provides a complete API for managing profiles, scheduling automated updates, and monitoring the automation process.

## **Key Features**

- **AI-Powered Content Generation**: Uses OpenAI GPT-3.5-turbo to generate professional therapist profile content
- **Automated Browser Interaction**: Playwright-based automation for profile updates
- **Secure Credential Management**: Fernet encryption for stored passwords
- **Scheduled Automation**: Weekly maintenance scheduler with configurable timing
- **Comprehensive Logging**: Detailed tracking of all automation activities
- **RESTful API**: Complete API for profile and automation management
- **JWT Authentication**: Secure API access with token-based authentication

## **System Architecture**

### **Core Components**
- **FastAPI Backend**: RESTful API with automatic documentation
- **SQLAlchemy ORM**: Database management with SQLite
- **Playwright Automation**: Browser automation for profile updates
- **OpenAI Integration**: AI content generation service
- **Schedule Management**: Automated task scheduling

### **Database Models**
- **User**: System users with JWT authentication
- **Profile**: Psychology Today profile credentials and status
- **UpdateLog**: Detailed logging of automation activities

## **API Endpoints**

### **Authentication**
```bash
# Login with form data
POST /api/auth/token
Content-Type: application/x-www-form-urlencoded
username=admin&password=password

# Login with JSON
POST /api/auth/login
{
  "username": "admin",
  "password": "password"
}

# Register new user
POST /api/auth/register
{
  "username": "newuser",
  "password": "password"
}

# Get current user info
GET /api/auth/me
Authorization: Bearer <token>
```

### **Profile Management**
```bash
# List all profiles
GET /api/profiles/
Authorization: Bearer <token>

# Create new profile
POST /api/profiles/
Authorization: Bearer <token>
{
  "pt_username": "john_therapist",
  "password": "secure_password",
  "is_active": true,
  "notes": "Optional notes"
}

# Get specific profile
GET /api/profiles/{profile_id}
Authorization: Bearer <token>

# Update profile
PUT /api/profiles/{profile_id}
Authorization: Bearer <token>
{
  "pt_username": "updated_username",
  "is_active": false,
  "notes": "Updated notes"
}

# Delete profile
DELETE /api/profiles/{profile_id}
Authorization: Bearer <token>
```

### **Automation Control**
```bash
# Start automation scheduler
POST /api/automation/start
Authorization: Bearer <token>

# Stop automation scheduler
POST /api/automation/stop
Authorization: Bearer <token>

# Run maintenance immediately
POST /api/automation/run-now
Authorization: Bearer <token>

# Get automation status
GET /api/automation/status
Authorization: Bearer <token>

# Get automation logs
GET /api/automation/logs?limit=50
Authorization: Bearer <token>
```

### **Update Logs**
```bash
# Get update logs
GET /api/update-logs/
Authorization: Bearer <token>

# Get logs for specific profile
GET /api/update-logs/profile/{profile_id}
Authorization: Bearer <token>
```

## **Automation Process**

### **Weekly Maintenance Cycle**
1. **Scheduler Activation**: Runs every 10 seconds (configurable)
2. **Active Profile Detection**: Identifies profiles with `is_active = True`
3. **Status Update**: Sets profile status to "Running"
4. **Password Decryption**: Securely retrieves stored credentials
5. **AI Content Generation**: Creates personalized profile content
6. **Browser Automation**: Updates profile using Playwright
7. **Status Tracking**: Records success/failure and timestamps
8. **Logging**: Creates detailed UpdateLog entries

### **AI Content Generation**
The system generates four key content sections:

```json
{
  "ideal_client": "500-580 character description of ideal client",
  "how_can_help": "200-330 character explanation of services",
  "empathy_invitation": "200-330 character invitation to reach out",
  "top_specialties": "200-320 character treatment specialties"
}
```

### **Profile Status Tracking**
- **Idle**: Profile waiting for next run
- **Running**: Currently being processed
- **Completed**: Successfully updated
- **Error**: Failed during processing
- **NoChange**: Processed but no changes made

### **Log Outcome Types**
- **Success**: Profile updated successfully with changes
- **Failure**: Profile update failed due to error
- **NoChange**: Profile processed but no fields were updated (content already optimal)
- **Warning**: Profile processed with warnings (future use)

### **Error Types and Handling**
The system handles different types of errors with specific strategies:

#### **Login Errors**
- **Invalid Credentials**: No retry, immediate failure
- **Account Locked**: No retry, immediate failure  
- **Too Many Attempts**: No retry, immediate failure
- **CAPTCHA Required**: No retry, immediate failure
- **Login Page Still Active**: No retry, immediate failure
- **Error Page Redirect**: No retry, immediate failure

#### **Navigation Errors**
- **Page Load Timeout**: Retry with longer delays (60s, 120s)
- **Network Issues**: Retry with longer delays
- **Website Unavailable**: Retry with exponential backoff

#### **Element Not Found Errors**
- **UI Structure Changes**: Retry with standard delays (30s, 60s)
- **Missing Fields**: Log warning, continue with other sections
- **Selector Changes**: Retry with standard delays

#### **Content Generation Errors**
- **OpenAI API Issues**: Immediate failure, no retry
- **Rate Limiting**: Immediate failure, no retry
- **Invalid Response**: Immediate failure, no retry

#### **Profile Update Errors**
- **Field Update Failures**: Continue with other sections
- **Save Failures**: Retry with standard delays
- **Validation Errors**: Log warning, continue

#### **NoChange Outcome**
- **Normal Behavior**: When content is already optimal
- **No Error**: This is not an error, just no updates needed
- **Successful Processing**: Profile was processed successfully

## **Setup Instructions**

### **1. Environment Setup**
```bash
# Clone repository
git clone <repository-url>
cd Profile-Automation-System

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### **2. Environment Variables**
Create a `.env` file in the root directory:
```env
# Database
DATABASE_URL=sqlite:///./app.db

# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key_here
FERNET_KEY=your_fernet_key_here

# JWT Settings
JWT_ACCESS_TOKEN_EXPIRE_DAYS=7

# Website URL
WEBSITE_URL=https://member.psychologytoday.com/us
```

### **3. Database Initialization**
```bash
# Create database tables
python create_tables.py

# Create admin user
python create_admin.py
```

### **4. Playwright Setup**
```bash
# Install Playwright browsers
playwright install
```

### **5. Start Application**
```bash
# Development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## **Configuration**

### **Scheduler Configuration**
The automation scheduler runs every 10 seconds by default. To modify:

```python
# In app/automation/weekly_maintenance.py
schedule.every(10).seconds.do(self.run_maintenance_now)
```

### **AI Content Settings**
- **Model**: GPT-3.5-turbo
- **Temperature**: 0.5 (balanced creativity)
- **Max Tokens**: 1000
- **Character Limits**: Strictly enforced for each section

### **Security Settings**
- **Password Encryption**: Fernet encryption for all stored passwords
- **JWT Token Expiry**: 7 days by default
- **API Authentication**: Required for all endpoints except login

## **Monitoring and Logging**

### **Automation Status**
```bash
# Check current status
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/automation/status
```

Response includes:
- Scheduler running status
- Active profile count
- Profile status distribution

### **Update Logs**
```bash
# Get recent logs
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/automation/logs?limit=50
```

Log entries include:
- Timestamp
- Profile ID
- Duration (milliseconds)
- Outcome (Success/Failure/NoChange)
- Fields edited
- Detailed log message

### **Profile Monitoring**
```bash
# List all profiles with status
curl -H "Authorization: Bearer <token>" \
     http://localhost:8000/api/profiles/
```

## **Troubleshooting**

### **Common Issues**

#### **1. Automation Not Starting**
- Check if scheduler is running: `GET /api/automation/status`
- Verify OpenAI API key is set correctly
- Check database connection

#### **2. Profile Login Failures**
- Verify Psychology Today credentials are correct
- Check if website structure has changed
- Review automation logs for specific errors

#### **3. AI Content Generation Errors**
- Verify OpenAI API key is valid
- Check internet connectivity
- Review API rate limits

#### **4. Database Issues**
- Ensure database file has write permissions
- Check if tables exist: `python create_tables.py`
- Verify SQLite installation

### **Debug Mode**
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Manual maintenance run
from app.automation.weekly_maintenance import run_maintenance_now
run_maintenance_now()
```

### **Log Analysis**
```bash
# Check recent automation logs
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/automation/logs?limit=100" | jq

# Filter for errors
curl -H "Authorization: Bearer <token>" \
     "http://localhost:8000/api/update-logs/" | jq '.data[] | select(.outcome == "Failure")'
```

## **Security Considerations**

### **Password Security**
- All passwords are encrypted using Fernet before storage
- Passwords are never stored in plain text
- Encryption key is stored in environment variables

### **API Security**
- JWT token authentication required for all endpoints
- Tokens expire after 7 days by default
- No sensitive data exposed in API responses

### **Data Protection**
- Database file should have restricted permissions
- Environment variables should be kept secure
- Regular backups recommended

## **Performance Optimization**

### **Automation Efficiency**
- 15-second delay between profile processing
- Retry mechanism (3 attempts) for failed operations
- Background thread processing for non-blocking operations

### **Database Optimization**
- Indexed primary keys for fast lookups
- Efficient query patterns for status updates
- Connection pooling for concurrent access

### **AI Content Caching**
- Content generation results are not cached (fresh content each time)
- Character limit validation prevents API waste
- Fallback content for API failures

## **Future Enhancements**

### **Planned Features**
- **Email Notifications**: Success/failure notifications
- **Web Dashboard**: User-friendly web interface
- **Advanced Scheduling**: Custom schedule configuration
- **Content Templates**: Pre-defined content templates
- **Analytics**: Performance metrics and reporting

### **Integration Possibilities**
- **Slack Notifications**: Team notification integration
- **Google Analytics**: Traffic tracking integration
- **CRM Integration**: Client management system integration
- **Multi-Platform Support**: Support for other therapist directories

## **API Documentation**

### **Interactive Documentation**
Once the application is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### **Response Format**
All API responses follow this format:
```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data here
  }
}
```

### **Error Handling**
```json
{
  "success": false,
  "message": "Error description",
  "data": null
}
```

## **Development Guidelines**

### **Code Structure**
```
app/
├── api/           # API endpoints
├── auth/          # Authentication logic
├── automation/    # Automation engine
├── models/        # Database models
├── schemas/       # Pydantic schemas
├── services/      # Business logic
└── utils/         # Utility functions
```

### **Adding New Features**
1. Create database models in `app/models/`
2. Define Pydantic schemas in `app/schemas/`
3. Implement business logic in `app/services/`
4. Add API endpoints in `app/api/`
5. Update documentation

### **Testing**
```bash
# Run tests (when implemented)
python -m pytest tests/

# Manual testing
curl -X POST "http://localhost:8000/api/automation/run-now" \
     -H "Authorization: Bearer <token>"
```

This comprehensive guide covers all aspects of the Psychology Today Profile Automation System, from setup and configuration to monitoring and troubleshooting. 