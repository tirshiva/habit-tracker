from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.habits.service import HabitService
from app.habits.schemas import HabitCreate, HabitUpdate, HabitResponse
from app.shared.dependencies import get_current_user
from app.shared.rate_limiter import get_rate_limiter
from slowapi import Limiter

router = APIRouter()
limiter = get_rate_limiter()


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_habit(
    habit_data: HabitCreate,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new habit"""
    habit_service = HabitService(db)
    return habit_service.create_habit(current_user.id, habit_data)


@router.get("", response_model=List[HabitResponse])
@limiter.limit("60/minute")
async def get_habits(
    request: Request,
    active_only: bool = False,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all habits for the current user"""
    habit_service = HabitService(db)
    return habit_service.get_user_habits(current_user.id, active_only)


@router.get("/{habit_id}", response_model=HabitResponse)
@limiter.limit("60/minute")
async def get_habit(
    habit_id: int,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific habit"""
    habit_service = HabitService(db)
    habit = habit_service.get_habit(habit_id, current_user.id)
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    return habit


@router.put("/{habit_id}", response_model=HabitResponse)
@limiter.limit("30/minute")
async def update_habit(
    habit_id: int,
    habit_data: HabitUpdate,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a habit"""
    habit_service = HabitService(db)
    return habit_service.update_habit(habit_id, current_user.id, habit_data)


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_habit(
    habit_id: int,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a habit"""
    habit_service = HabitService(db)
    habit_service.delete_habit(habit_id, current_user.id)
    return None

