from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class UserPreference(Base):
    __tablename__ = "user_preferences"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    timezone = Column(String, default="UTC")
    language = Column(String, default="en")
    theme = Column(String, default="light")  # light, dark, auto
    email_notifications = Column(Boolean, default=True)
    push_notifications = Column(Boolean, default=True)
    reminder_enabled = Column(Boolean, default=True)
    weekly_report = Column(Boolean, default=True)
    settings = Column(JSON, nullable=True)  # Additional flexible settings
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="preferences")

