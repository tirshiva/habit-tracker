from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.analytics.service import AnalyticsService
from app.analytics.schemas import AnalyticsResponse, StreakResponse
from app.shared.dependencies import get_current_user
from app.shared.rate_limiter import get_rate_limiter
from slowapi import Limiter

router = APIRouter()
limiter = get_rate_limiter()


@router.get("", response_model=AnalyticsResponse)
@limiter.limit("60/minute")
async def get_analytics(
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive analytics for the current user"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_analytics(current_user.id)


@router.get("/streaks", response_model=List[StreakResponse])
@limiter.limit("60/minute")
async def get_streaks(
    request: Request,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all streaks for the current user"""
    analytics_service = AnalyticsService(db)
    return analytics_service.get_streaks(current_user.id)

