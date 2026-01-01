from sqlalchemy.orm import Session
from app.analytics.repository import AnalyticsRepository
from app.habits.repository import HabitRepository
from app.analytics.schemas import AnalyticsResponse, StreakResponse, HabitStats
from app.redis_client import get_cache, set_cache
from typing import List, Dict
from datetime import date, timedelta


class AnalyticsService:
    def __init__(self, db: Session):
        self.analytics_repo = AnalyticsRepository(db)
        self.habit_repo = HabitRepository(db)
        self.db = db
    
    def get_analytics(self, user_id: int) -> dict:
        """Get comprehensive analytics for a user"""
        cache_key = f"analytics:user:{user_id}"
        cached_analytics = get_cache(cache_key)
        if cached_analytics:
            return cached_analytics
        
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        month_start = date(today.year, today.month, 1)
        
        # Get basic stats
        total_habits = self.analytics_repo.get_total_habits(user_id)
        active_habits = self.analytics_repo.get_active_habits(user_id)
        total_completions = self.analytics_repo.get_completion_count(user_id, date(2000, 1, 1), today)
        completions_this_week = self.analytics_repo.get_completion_count(user_id, week_start, today)
        completions_this_month = self.analytics_repo.get_completion_count(user_id, month_start, today)
        
        # Calculate completion rate (completions / (active_habits * days))
        days_since_start = (today - month_start).days + 1
        expected_completions = active_habits * days_since_start if active_habits > 0 else 1
        overall_completion_rate = (completions_this_month / expected_completions * 100) if expected_completions > 0 else 0
        
        # Get streaks
        streaks_data = self.analytics_repo.get_user_streaks(user_id)
        streaks = []
        for streak in streaks_data:
            habit = self.habit_repo.get_by_id(streak.habit_id, user_id)
            if habit:
                streaks.append({
                    "habit_id": streak.habit_id,
                    "habit_name": habit.name,
                    "current_streak": streak.current_streak,
                    "longest_streak": streak.longest_streak,
                    "last_completion_date": streak.last_completion_date.isoformat() if streak.last_completion_date else None,
                    "streak_start_date": streak.streak_start_date.isoformat() if streak.streak_start_date else None
                })
        
        # Get habit stats
        habits = self.habit_repo.get_all_by_user(user_id, active_only=True)
        habit_stats = []
        for habit in habits:
            habit_completions = self.analytics_repo.get_habit_completion_count(user_id, habit.id, month_start, today)
            streak = self.analytics_repo.get_habit_streak(user_id, habit.id)
            
            days_since_habit_start = (today - habit.created_at.date()).days + 1 if habit.created_at else 1
            completion_rate = (habit_completions / days_since_habit_start * 100) if days_since_habit_start > 0 else 0
            
            habit_stats.append({
                "habit_id": habit.id,
                "habit_name": habit.name,
                "total_completions": habit_completions,
                "current_streak": streak.current_streak if streak else 0,
                "longest_streak": streak.longest_streak if streak else 0,
                "completion_rate": completion_rate,
                "last_completion_date": streak.last_completion_date.isoformat() if streak and streak.last_completion_date else None
            })
        
        # Get weekly and monthly completion charts
        weekly_completions = self.analytics_repo.get_weekly_completions(user_id, week_start)
        monthly_completions = self.analytics_repo.get_monthly_completions(user_id, month_start)
        
        analytics_data = {
            "total_habits": total_habits,
            "active_habits": active_habits,
            "total_completions": total_completions,
            "completions_this_week": completions_this_week,
            "completions_this_month": completions_this_month,
            "overall_completion_rate": round(overall_completion_rate, 2),
            "streaks": streaks,
            "habit_stats": habit_stats,
            "weekly_completions": weekly_completions,
            "monthly_completions": monthly_completions
        }
        
        # Cache for 15 minutes
        set_cache(cache_key, analytics_data, expire=900)
        return analytics_data
    
    def get_streaks(self, user_id: int) -> List[dict]:
        """Get all streaks for a user"""
        cache_key = f"streaks:user:{user_id}"
        cached_streaks = get_cache(cache_key)
        if cached_streaks:
            return cached_streaks
        
        streaks_data = self.analytics_repo.get_user_streaks(user_id)
        streaks = []
        for streak in streaks_data:
            habit = self.habit_repo.get_by_id(streak.habit_id, user_id)
            if habit:
                streaks.append({
                    "habit_id": streak.habit_id,
                    "habit_name": habit.name,
                    "current_streak": streak.current_streak,
                    "longest_streak": streak.longest_streak,
                    "last_completion_date": streak.last_completion_date.isoformat() if streak.last_completion_date else None,
                    "streak_start_date": streak.streak_start_date.isoformat() if streak.streak_start_date else None
                })
        
        # Cache for 10 minutes
        set_cache(cache_key, streaks, expire=600)
        return streaks

