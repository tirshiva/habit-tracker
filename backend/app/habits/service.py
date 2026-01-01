from sqlalchemy.orm import Session
from app.habits.repository import HabitRepository
from app.habits.schemas import HabitCreate, HabitUpdate
from app.redis_client import get_cache, set_cache, delete_cache, delete_cache_pattern
from fastapi import HTTPException, status
from typing import List, Optional


class HabitService:
    def __init__(self, db: Session):
        self.habit_repo = HabitRepository(db)
        self.db = db
    
    def create_habit(self, user_id: int, habit_data: HabitCreate) -> dict:
        """Create a new habit"""
        habit_dict = habit_data.model_dump()
        habit_dict["user_id"] = user_id
        
        habit = self.habit_repo.create(habit_dict)
        
        # Invalidate cache
        delete_cache_pattern(f"habits:user:{user_id}:*")
        delete_cache(f"habit:{habit.id}")
        
        return {
            "id": habit.id,
            "user_id": habit.user_id,
            "name": habit.name,
            "description": habit.description,
            "frequency": habit.frequency.value,
            "target_days": habit.target_days,
            "color": habit.color,
            "icon": habit.icon,
            "is_active": habit.is_active,
            "reminder_time": habit.reminder_time,
            "created_at": habit.created_at.isoformat(),
            "updated_at": habit.updated_at.isoformat()
        }
    
    def get_habit(self, habit_id: int, user_id: int) -> Optional[dict]:
        """Get a habit by ID"""
        # Try cache first
        cache_key = f"habit:{habit_id}"
        cached_habit = get_cache(cache_key)
        if cached_habit and cached_habit.get("user_id") == user_id:
            return cached_habit
        
        habit = self.habit_repo.get_by_id(habit_id, user_id)
        if not habit:
            return None
        
        habit_dict = {
            "id": habit.id,
            "user_id": habit.user_id,
            "name": habit.name,
            "description": habit.description,
            "frequency": habit.frequency.value,
            "target_days": habit.target_days,
            "color": habit.color,
            "icon": habit.icon,
            "is_active": habit.is_active,
            "reminder_time": habit.reminder_time,
            "created_at": habit.created_at.isoformat(),
            "updated_at": habit.updated_at.isoformat()
        }
        
        # Cache for 1 hour
        set_cache(cache_key, habit_dict, expire=3600)
        return habit_dict
    
    def get_user_habits(self, user_id: int, active_only: bool = False) -> List[dict]:
        """Get all habits for a user"""
        cache_key = f"habits:user:{user_id}:active:{active_only}"
        cached_habits = get_cache(cache_key)
        if cached_habits:
            return cached_habits
        
        habits = self.habit_repo.get_all_by_user(user_id, active_only)
        habits_list = [
            {
                "id": habit.id,
                "user_id": habit.user_id,
                "name": habit.name,
                "description": habit.description,
                "frequency": habit.frequency.value,
                "target_days": habit.target_days,
                "color": habit.color,
                "icon": habit.icon,
                "is_active": habit.is_active,
                "reminder_time": habit.reminder_time,
                "created_at": habit.created_at.isoformat(),
                "updated_at": habit.updated_at.isoformat()
            }
            for habit in habits
        ]
        
        # Cache for 30 minutes
        set_cache(cache_key, habits_list, expire=1800)
        return habits_list
    
    def update_habit(self, habit_id: int, user_id: int, habit_data: HabitUpdate) -> dict:
        """Update a habit"""
        habit = self.habit_repo.get_by_id(habit_id, user_id)
        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found"
            )
        
        update_data = habit_data.model_dump(exclude_unset=True)
        habit = self.habit_repo.update(habit, update_data)
        
        # Invalidate cache
        delete_cache(f"habit:{habit.id}")
        delete_cache_pattern(f"habits:user:{user_id}:*")
        
        return {
            "id": habit.id,
            "user_id": habit.user_id,
            "name": habit.name,
            "description": habit.description,
            "frequency": habit.frequency.value,
            "target_days": habit.target_days,
            "color": habit.color,
            "icon": habit.icon,
            "is_active": habit.is_active,
            "reminder_time": habit.reminder_time,
            "created_at": habit.created_at.isoformat(),
            "updated_at": habit.updated_at.isoformat()
        }
    
    def delete_habit(self, habit_id: int, user_id: int) -> bool:
        """Delete a habit"""
        habit = self.habit_repo.get_by_id(habit_id, user_id)
        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found"
            )
        
        # Invalidate cache
        delete_cache(f"habit:{habit.id}")
        delete_cache_pattern(f"habits:user:{user_id}:*")
        delete_cache_pattern(f"streaks:user:{user_id}:habit:{habit_id}:*")
        
        return self.habit_repo.delete(habit)

