from sqlalchemy.orm import Session
from app.habits.models import Habit
from typing import List, Optional


class HabitRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, habit_id: int, user_id: int) -> Optional[Habit]:
        """Get habit by ID for a specific user"""
        return self.db.query(Habit).filter(
            Habit.id == habit_id,
            Habit.user_id == user_id
        ).first()
    
    def get_all_by_user(self, user_id: int, active_only: bool = False) -> List[Habit]:
        """Get all habits for a user"""
        query = self.db.query(Habit).filter(Habit.user_id == user_id)
        if active_only:
            query = query.filter(Habit.is_active == True)
        return query.order_by(Habit.created_at.desc()).all()
    
    def create(self, habit_data: dict) -> Habit:
        """Create a new habit"""
        habit = Habit(**habit_data)
        self.db.add(habit)
        self.db.commit()
        self.db.refresh(habit)
        return habit
    
    def update(self, habit: Habit, habit_data: dict) -> Habit:
        """Update habit"""
        for key, value in habit_data.items():
            if value is not None:
                setattr(habit, key, value)
        self.db.commit()
        self.db.refresh(habit)
        return habit
    
    def delete(self, habit: Habit) -> bool:
        """Delete habit"""
        self.db.delete(habit)
        self.db.commit()
        return True

