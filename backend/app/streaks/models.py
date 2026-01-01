from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, date


class Streak(Base):
    __tablename__ = "streaks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False, index=True)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_completion_date = Column(Date, nullable=True)
    streak_start_date = Column(Date, nullable=True)
    last_calculated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="streaks")
    habit = relationship("Habit", back_populates="streaks")
    
    # Unique constraint on user_id and habit_id
    __table_args__ = (
        UniqueConstraint('user_id', 'habit_id', name='uq_user_habit_streak'),
    )

