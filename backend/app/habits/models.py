from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime
import enum


class HabitFrequency(str, enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    CUSTOM = "custom"


class Habit(Base):
    __tablename__ = "habits"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    frequency = Column(Enum(HabitFrequency), default=HabitFrequency.DAILY)
    target_days = Column(String, nullable=True)  # For custom frequency, e.g., "1,3,5" for Mon,Wed,Fri
    color = Column(String, default="#3B82F6")  # Hex color code
    icon = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    reminder_time = Column(String, nullable=True)  # HH:MM format
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="habits")
    completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")
    streaks = relationship("Streak", back_populates="habit", cascade="all, delete-orphan")

