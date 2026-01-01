from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.database import get_db
from app.completions.service import HabitCompletionService
from app.completions.schemas import HabitCompletionCreate, HabitCompletionUpdate, HabitCompletionResponse
from app.shared.dependencies import get_current_user
from app.shared.rate_limiter import get_rate_limiter
from slowapi import Limiter

router = APIRouter()
limiter = get_rate_limiter()


@router.post("", response_model=HabitCompletionResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("60/minute")
async def create_completion(
    completion_data: HabitCompletionCreate,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new habit completion"""
    completion_service = HabitCompletionService(db)
    return completion_service.create_completion(current_user.id, completion_data)


@router.get("/habit/{habit_id}", response_model=List[HabitCompletionResponse])
@limiter.limit("60/minute")
async def get_habit_completions(
    habit_id: int,
    request: Request,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all completions for a specific habit"""
    completion_service = HabitCompletionService(db)
    return completion_service.get_habit_completions(
        current_user.id,
        habit_id,
        start_date,
        end_date
    )


@router.get("/{completion_id}", response_model=HabitCompletionResponse)
@limiter.limit("60/minute")
async def get_completion(
    completion_id: int,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific completion"""
    completion_service = HabitCompletionService(db)
    completion = completion_service.get_completion(completion_id, current_user.id)
    if not completion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Completion not found"
        )
    return completion


@router.put("/{completion_id}", response_model=HabitCompletionResponse)
@limiter.limit("30/minute")
async def update_completion(
    completion_id: int,
    completion_data: HabitCompletionUpdate,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a completion"""
    completion_service = HabitCompletionService(db)
    return completion_service.update_completion(completion_id, current_user.id, completion_data)


@router.delete("/{completion_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def delete_completion(
    completion_id: int,
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a completion"""
    completion_service = HabitCompletionService(db)
    completion_service.delete_completion(completion_id, current_user.id)
    return None

