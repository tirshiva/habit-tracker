from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.habits.models import Habit
from app.completions.models import HabitCompletion
from app.streaks.models import Streak
from typing import List, Dict
from datetime import date, timedelta


class AnalyticsRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_streaks(self, user_id: int) -> List[Streak]:
        """Get all streaks for a user"""
        return self.db.query(Streak).filter(
            Streak.user_id == user_id
        ).all()
    
    def get_habit_streak(self, user_id: int, habit_id: int) -> Streak:
        """Get streak for a specific habit"""
        return self.db.query(Streak).filter(
            Streak.user_id == user_id,
            Streak.habit_id == habit_id
        ).first()
    
    def get_completion_count(self, user_id: int, start_date: date, end_date: date) -> int:
        """Get completion count for a date range"""
        return self.db.query(func.count(HabitCompletion.id)).filter(
            HabitCompletion.user_id == user_id,
            HabitCompletion.completion_date >= start_date,
            HabitCompletion.completion_date <= end_date
        ).scalar() or 0
    
    def get_habit_completion_count(self, user_id: int, habit_id: int, start_date: date, end_date: date) -> int:
        """Get completion count for a habit in a date range"""
        return self.db.query(func.count(HabitCompletion.id)).filter(
            HabitCompletion.user_id == user_id,
            HabitCompletion.habit_id == habit_id,
            HabitCompletion.completion_date >= start_date,
            HabitCompletion.completion_date <= end_date
        ).scalar() or 0
    
    def get_weekly_completions(self, user_id: int, start_date: date) -> Dict[str, int]:
        """Get daily completion counts for a week"""
        end_date = start_date + timedelta(days=6)
        completions = self.db.query(
            func.date(HabitCompletion.completion_date).label('date'),
            func.count(HabitCompletion.id).label('count')
        ).filter(
            HabitCompletion.user_id == user_id,
            HabitCompletion.completion_date >= start_date,
            HabitCompletion.completion_date <= end_date
        ).group_by(func.date(HabitCompletion.completion_date)).all()
        
        return {str(row.date): row.count for row in completions}
    
    def get_monthly_completions(self, user_id: int, start_date: date) -> Dict[str, int]:
        """Get daily completion counts for a month"""
        # Calculate end of month
        if start_date.month == 12:
            end_date = date(start_date.year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(start_date.year, start_date.month + 1, 1) - timedelta(days=1)
        
        completions = self.db.query(
            func.date(HabitCompletion.completion_date).label('date'),
            func.count(HabitCompletion.id).label('count')
        ).filter(
            HabitCompletion.user_id == user_id,
            HabitCompletion.completion_date >= start_date,
            HabitCompletion.completion_date <= end_date
        ).group_by(func.date(HabitCompletion.completion_date)).all()
        
        return {str(row.date): row.count for row in completions}
    
    def get_total_habits(self, user_id: int) -> int:
        """Get total number of habits"""
        return self.db.query(func.count(Habit.id)).filter(
            Habit.user_id == user_id
        ).scalar() or 0
    
    def get_active_habits(self, user_id: int) -> int:
        """Get number of active habits"""
        return self.db.query(func.count(Habit.id)).filter(
            Habit.user_id == user_id,
            Habit.is_active == True
        ).scalar() or 0

