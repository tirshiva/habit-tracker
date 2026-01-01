from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.habits.repository import HabitRepository
from app.completions.repository import HabitCompletionRepository
from app.streaks.models import Streak
from app.redis_client import delete_cache_pattern
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


def calculate_streak_for_habit(db: Session, user_id: int, habit_id: int):
    """Calculate streak for a specific habit"""
    try:
        completion_repo = HabitCompletionRepository(db)
        habit_repo = HabitRepository(db)
        
        # Get all completions for this habit, ordered by date
        completions = completion_repo.get_by_habit(user_id, habit_id)
        completion_dates = sorted([c.completion_date for c in completions], reverse=True)
        
        if not completion_dates:
            # No completions, reset streak
            streak = db.query(Streak).filter(
                Streak.user_id == user_id,
                Streak.habit_id == habit_id
            ).first()
            
            if streak:
                streak.current_streak = 0
                streak.last_completion_date = None
                streak.streak_start_date = None
                db.commit()
            return
        
        # Calculate current streak
        today = date.today()
        current_streak = 0
        longest_streak = 0
        last_completion_date = completion_dates[0]
        streak_start_date = None
        
        # Calculate longest streak
        temp_streak = 1
        longest_start = completion_dates[0]
        for i in range(1, len(completion_dates)):
            if (completion_dates[i-1] - completion_dates[i]).days == 1:
                temp_streak += 1
            else:
                if temp_streak > longest_streak:
                    longest_streak = temp_streak
                temp_streak = 1
        if temp_streak > longest_streak:
            longest_streak = temp_streak
        
        # Calculate current streak from today backwards
        expected_date = today
        for completion_date in completion_dates:
            if completion_date == expected_date or completion_date == expected_date - timedelta(days=1):
                if current_streak == 0:
                    streak_start_date = completion_date
                current_streak += 1
                expected_date = completion_date - timedelta(days=1)
            elif completion_date < expected_date:
                break
        
        # Get or create streak record
        streak = db.query(Streak).filter(
            Streak.user_id == user_id,
            Streak.habit_id == habit_id
        ).first()
        
        if not streak:
            streak = Streak(
                user_id=user_id,
                habit_id=habit_id,
                current_streak=current_streak,
                longest_streak=longest_streak,
                last_completion_date=last_completion_date,
                streak_start_date=streak_start_date
            )
            db.add(streak)
        else:
            streak.current_streak = current_streak
            streak.longest_streak = max(streak.longest_streak, longest_streak)
            streak.last_completion_date = last_completion_date
            streak.streak_start_date = streak_start_date
        
        db.commit()
        
        # Invalidate cache
        delete_cache_pattern(f"streaks:user:{user_id}:habit:{habit_id}:*")
        delete_cache_pattern(f"analytics:user:{user_id}")
        
        logger.info(f"Calculated streak for user {user_id}, habit {habit_id}: {current_streak}")
        
    except Exception as e:
        logger.error(f"Error calculating streak: {e}")
        db.rollback()


def calculate_all_streaks():
    """Calculate streaks for all active habits"""
    db = None
    try:
        db = SessionLocal()
        # Get all active habits
        from app.habits.models import Habit
        habits = db.query(Habit).filter(Habit.is_active == True).all()
        
        for habit in habits:
            calculate_streak_for_habit(db, habit.user_id, habit.id)
        
        logger.info("Completed streak calculation for all habits")
    except Exception as e:
        logger.error(f"Error in calculate_all_streaks: {e}", exc_info=True)
    finally:
        if db:
            try:
                db.close()
            except Exception as e:
                logger.error(f"Error closing database session: {e}")


def start_streak_calculator():
    """Start the streak calculator scheduler"""
    scheduler = BackgroundScheduler()
    
    # Run every hour
    scheduler.add_job(
        calculate_all_streaks,
        trigger=CronTrigger(minute=0),  # Run at the top of every hour
        id='streak_calculator',
        name='Calculate streaks for all habits',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Streak calculator scheduler started")

