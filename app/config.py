"""
config.py
Configuration and environment variable management for the application.
Loads all sensitive and environment-specific values from the .env file using pydantic-settings.
"""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables (.env file).
    """
    # FastAPI settings
    APP_NAME: str = "Psychology Today Profile Automation System"
    DEBUG: bool = False

    # Database settings
    DATABASE_URL: str = "sqlite:///./app.db"


    
    # SMTP settings for email notifications
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USERNAME: str = "amy@wickerpsychotherapy.com"
    SMTP_PASSWORD: str = "zwpx ryzx clvo ojos"
    SENDER_EMAIL: str = "amy@wickerpsychotherapy.com"
    SENDER_NAME: str = "Profile Automation System"
    ADMIN_EMAIL: str = "amy@wickerpsychotherapy.com"

    # AI API settings
    OPENAI_API_KEY: str = "your-openai-api-key"

    # Security
    SECRET_KEY: str = "supersecretkey"

    # Website URL (for Playwright automation)
    WEBSITE_URL: str = "https://member.psychologytoday.com/us"

    # JWT settings
    JWT_SECRET_KEY: str = "ffb19aca7633703907f6996fa150cdd3f32c79c46aa8c6247b638a9b506ed6e6"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 600  # keep for backward compatibility
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = 7
    
    # Fernet key
    FERNET_KEY: str = "lY7hqXWoFo1Rz8oSbSZEFuEIwX3G4G3bIcDUaAXBgR4="

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Singleton settings instance
settings = Settings() 