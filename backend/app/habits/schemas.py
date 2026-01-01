from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.habits.models import HabitFrequency


class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    frequency: HabitFrequency = HabitFrequency.DAILY
    target_days: Optional[str] = None
    color: str = "#3B82F6"
    icon: Optional[str] = None
    reminder_time: Optional[str] = None


class HabitUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    frequency: Optional[HabitFrequency] = None
    target_days: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: Optional[bool] = None
    reminder_time: Optional[str] = None


class HabitResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    frequency: HabitFrequency
    target_days: Optional[str]
    color: str
    icon: Optional[str]
    is_active: bool
    reminder_time: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

