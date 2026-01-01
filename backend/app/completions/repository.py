from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.completions.models import HabitCompletion
from typing import List, Optional
from datetime import date, datetime, timedelta


class HabitCompletionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, completion_id: int, user_id: int) -> Optional[HabitCompletion]:
        """Get completion by ID for a specific user"""
        return self.db.query(HabitCompletion).filter(
            HabitCompletion.id == completion_id,
            HabitCompletion.user_id == user_id
        ).first()
    
    def get_by_date(self, user_id: int, habit_id: int, completion_date: date) -> Optional[HabitCompletion]:
        """Get completion for a specific date"""
        return self.db.query(HabitCompletion).filter(
            HabitCompletion.user_id == user_id,
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completion_date == completion_date
        ).first()
    
    def get_by_habit(self, user_id: int, habit_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[HabitCompletion]:
        """Get all completions for a habit"""
        query = self.db.query(HabitCompletion).filter(
            HabitCompletion.user_id == user_id,
            HabitCompletion.habit_id == habit_id
        )
        
        if start_date:
            query = query.filter(HabitCompletion.completion_date >= start_date)
        if end_date:
            query = query.filter(HabitCompletion.completion_date <= end_date)
        
        return query.order_by(HabitCompletion.completion_date.desc()).all()
    
    def get_by_user(self, user_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[HabitCompletion]:
        """Get all completions for a user"""
        query = self.db.query(HabitCompletion).filter(
            HabitCompletion.user_id == user_id
        )
        
        if start_date:
            query = query.filter(HabitCompletion.completion_date >= start_date)
        if end_date:
            query = query.filter(HabitCompletion.completion_date <= end_date)
        
        return query.order_by(HabitCompletion.completion_date.desc()).all()
    
    def create(self, completion_data: dict) -> HabitCompletion:
        """Create a new completion"""
        completion = HabitCompletion(**completion_data)
        self.db.add(completion)
        self.db.commit()
        self.db.refresh(completion)
        return completion
    
    def update(self, completion: HabitCompletion, completion_data: dict) -> HabitCompletion:
        """Update completion"""
        for key, value in completion_data.items():
            if value is not None:
                setattr(completion, key, value)
        self.db.commit()
        self.db.refresh(completion)
        return completion
    
    def delete(self, completion: HabitCompletion) -> bool:
        """Delete completion"""
        self.db.delete(completion)
        self.db.commit()
        return True
    
    def get_completion_count(self, user_id: int, habit_id: int, start_date: date, end_date: date) -> int:
        """Get completion count for a date range"""
        return self.db.query(func.count(HabitCompletion.id)).filter(
            HabitCompletion.user_id == user_id,
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completion_date >= start_date,
            HabitCompletion.completion_date <= end_date
        ).scalar() or 0

