from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import date


class StreakResponse(BaseModel):
    habit_id: int
    habit_name: str
    current_streak: int
    longest_streak: int
    last_completion_date: Optional[date]
    streak_start_date: Optional[date]


class CompletionStats(BaseModel):
    total_completions: int
    completions_this_week: int
    completions_this_month: int
    completion_rate: float  # Percentage


class HabitStats(BaseModel):
    habit_id: int
    habit_name: str
    total_completions: int
    current_streak: int
    longest_streak: int
    completion_rate: float
    last_completion_date: Optional[date]


class AnalyticsResponse(BaseModel):
    total_habits: int
    active_habits: int
    total_completions: int
    completions_this_week: int
    completions_this_month: int
    overall_completion_rate: float
    streaks: List[StreakResponse]
    habit_stats: List[HabitStats]
    weekly_completions: Dict[str, int]  # Date -> count
    monthly_completions: Dict[str, int]  # Date -> count

