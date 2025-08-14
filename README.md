# Psychology Today Profile Automation System

AI-powered automation system for maintaining Psychology Today therapist profiles. Built with FastAPI, Selenium/Playwright, and OpenAI integration.

## Features
- Automates weekly updates for ~30 therapist profiles
- AI-generated, human-like content variations
- Realistic browser automation (delays, typing cadence)
- Secure credential storage (single password, encrypted)
- Web dashboard for monitoring, control, and error reporting
- Email notifications for errors and completion summaries

## Project Structure
```
app/
  ├── __init__.py
  ├── main.py            # FastAPI entrypoint
  ├── config.py          # Environment/config management
  ├── models/            # ORM/data models
  ├── schemas/           # Pydantic schemas
  ├── services/          # Business logic (AI, scheduling, etc.)
  ├── automation/        # Browser automation scripts
  ├── dashboard/         # Web dashboard routes
  ├── auth/              # Authentication logic
  ├── notifications/     # Email notification logic
  ├── utils/             # Utility functions
  └── api/               # API routers
      └── router.py      # Main API router

requirements.txt         # Python dependencies
.env.example             # Example environment variables
tests/                   # Unit/integration tests
```

## Getting Started
1. **Clone the repo**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables**
   - Copy `.env.example` to `.env` and fill in your values
4. **Run the app**
   ```bash
   uvicorn app.main:app --reload
   ```
5. **Access the API/docs**
   - Visit [http://localhost:8000/docs](http://localhost:8000/docs)

## Core Technologies
- **FastAPI**: Web framework
- **Selenium/Playwright**: Browser automation
- **OpenAI**: AI content generation
- **SQLAlchemy**: Database ORM
- **Alembic**: Migrations
- **Jinja2**: Dashboard templating

## Security
- Credentials encrypted at rest
- Single user authentication (no multi-user/roles)
- No HIPAA requirements

## Contact
For questions, contact Amy Wicker (practice owner). 