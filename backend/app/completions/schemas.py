from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime


class HabitCompletionCreate(BaseModel):
    habit_id: int
    completion_date: date
    notes: Optional[str] = None


class HabitCompletionUpdate(BaseModel):
    notes: Optional[str] = None


class HabitCompletionResponse(BaseModel):
    id: int
    user_id: int
    habit_id: int
    completion_date: date
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

