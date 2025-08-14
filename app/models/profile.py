"""
profile.py
SQLAlchemy model for Psychology Today profiles management.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from cryptography.fernet import Fernet
import os
from app.config import settings
# Use the same Base as other models
from app.models.user import Base

# Encryption key for passwords
FERNET_KEY = settings.FERNET_KEY
if not FERNET_KEY:
    FERNET_KEY = Fernet.generate_key().decode()
    print(f"[WARNING] No FERNET_KEY found in environment. Generated: {FERNET_KEY}")
fernet = Fernet(FERNET_KEY.encode())

class Profile(Base):
    __tablename__ = "profiles"

    profile_id = Column(Integer, primary_key=True, index=True)
    pt_username = Column(String, unique=True, nullable=False)
    _encrypted_password = Column("encrypted_password", String, nullable=False)
    is_active = Column(Boolean, default=True)
    status = Column(String, default="Idle")
    last_run_at = Column(DateTime(timezone=True))
    last_success_at = Column(DateTime(timezone=True))
    next_run_at = Column(DateTime(timezone=True))
    notes = Column(Text)

    # Relationship with UpdateLog
    update_logs = relationship("UpdateLog", back_populates="profile")

    def set_password(self, raw_password: str):
        """Encrypt and store the password."""
        self._encrypted_password = fernet.encrypt(raw_password.encode()).decode()

    def get_password(self) -> str:
        try:
            return fernet.decrypt(self._encrypted_password.encode()).decode()
        except Exception as e:
            print(f"Password decrypt error for {self.pt_username}: {type(e).__name__}: {e}")
            return ""

    def __repr__(self):
        return f"<Profile(pt_username={self.pt_username}, status={self.status})>" 