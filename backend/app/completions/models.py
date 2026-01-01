from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, date


class HabitCompletion(Base):
    __tablename__ = "habit_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False, index=True)
    completion_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="completions")
    habit = relationship("Habit", back_populates="completions")
    
    # Unique constraint on user_id, habit_id, and completion_date
    __table_args__ = (
        UniqueConstraint('user_id', 'habit_id', 'completion_date', name='uq_user_habit_date'),
    )

