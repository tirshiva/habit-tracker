from sqlalchemy.orm import Session
from app.completions.repository import HabitCompletionRepository
from app.habits.repository import HabitRepository
from app.completions.schemas import HabitCompletionCreate, HabitCompletionUpdate
from app.redis_client import get_cache, set_cache, delete_cache, delete_cache_pattern
from fastapi import HTTPException, status
from typing import List, Optional
from datetime import date, timedelta


class HabitCompletionService:
    def __init__(self, db: Session):
        self.completion_repo = HabitCompletionRepository(db)
        self.habit_repo = HabitRepository(db)
        self.db = db
    
    def create_completion(self, user_id: int, completion_data: HabitCompletionCreate) -> dict:
        """Create a new completion"""
        # Verify habit belongs to user
        habit = self.habit_repo.get_by_id(completion_data.habit_id, user_id)
        if not habit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Habit not found"
            )
        
        # Check if completion already exists for this date
        existing = self.completion_repo.get_by_date(
            user_id,
            completion_data.habit_id,
            completion_data.completion_date
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Completion already exists for this date"
            )
        
        completion_dict = completion_data.model_dump()
        completion_dict["user_id"] = user_id
        
        completion = self.completion_repo.create(completion_dict)
        
        # Invalidate cache
        delete_cache_pattern(f"completions:user:{user_id}:*")
        delete_cache_pattern(f"streaks:user:{user_id}:habit:{completion_data.habit_id}:*")
        
        return {
            "id": completion.id,
            "user_id": completion.user_id,
            "habit_id": completion.habit_id,
            "completion_date": completion.completion_date.isoformat(),
            "notes": completion.notes,
            "created_at": completion.created_at.isoformat(),
            "updated_at": completion.updated_at.isoformat()
        }
    
    def get_completion(self, completion_id: int, user_id: int) -> Optional[dict]:
        """Get a completion by ID"""
        completion = self.completion_repo.get_by_id(completion_id, user_id)
        if not completion:
            return None
        
        return {
            "id": completion.id,
            "user_id": completion.user_id,
            "habit_id": completion.habit_id,
            "completion_date": completion.completion_date.isoformat(),
            "notes": completion.notes,
            "created_at": completion.created_at.isoformat(),
            "updated_at": completion.updated_at.isoformat()
        }
    
    def get_habit_completions(
        self,
        user_id: int,
        habit_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[dict]:
        """Get all completions for a habit"""
        cache_key = f"completions:user:{user_id}:habit:{habit_id}:{start_date}:{end_date}"
        cached_completions = get_cache(cache_key)
        if cached_completions:
            return cached_completions
        
        completions = self.completion_repo.get_by_habit(user_id, habit_id, start_date, end_date)
        completions_list = [
            {
                "id": completion.id,
                "user_id": completion.user_id,
                "habit_id": completion.habit_id,
                "completion_date": completion.completion_date.isoformat(),
                "notes": completion.notes,
                "created_at": completion.created_at.isoformat(),
                "updated_at": completion.updated_at.isoformat()
            }
            for completion in completions
        ]
        
        # Cache for 15 minutes
        set_cache(cache_key, completions_list, expire=900)
        return completions_list
    
    def update_completion(
        self,
        completion_id: int,
        user_id: int,
        completion_data: HabitCompletionUpdate
    ) -> dict:
        """Update a completion"""
        completion = self.completion_repo.get_by_id(completion_id, user_id)
        if not completion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Completion not found"
            )
        
        update_data = completion_data.model_dump(exclude_unset=True)
        completion = self.completion_repo.update(completion, update_data)
        
        # Invalidate cache
        delete_cache_pattern(f"completions:user:{user_id}:*")
        delete_cache_pattern(f"streaks:user:{user_id}:habit:{completion.habit_id}:*")
        
        return {
            "id": completion.id,
            "user_id": completion.user_id,
            "habit_id": completion.habit_id,
            "completion_date": completion.completion_date.isoformat(),
            "notes": completion.notes,
            "created_at": completion.created_at.isoformat(),
            "updated_at": completion.updated_at.isoformat()
        }
    
    def delete_completion(self, completion_id: int, user_id: int) -> bool:
        """Delete a completion"""
        completion = self.completion_repo.get_by_id(completion_id, user_id)
        if not completion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Completion not found"
            )
        
        habit_id = completion.habit_id
        
        # Invalidate cache
        delete_cache_pattern(f"completions:user:{user_id}:*")
        delete_cache_pattern(f"streaks:user:{user_id}:habit:{habit_id}:*")
        
        return self.completion_repo.delete(completion)

