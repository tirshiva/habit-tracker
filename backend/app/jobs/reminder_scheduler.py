from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.habits.repository import HabitRepository
from app.preferences.models import UserPreference
from app.completions.repository import HabitCompletionRepository
from datetime import date, datetime, time
import logging

logger = logging.getLogger(__name__)


def send_reminder(user_id: int, habit_id: int, habit_name: str, reminder_time: str):
    """Send reminder for a habit (placeholder for email/push notification)"""
    try:
        # TODO: Integrate with email service (SendGrid, SES) or push notification service
        # For now, just log the reminder
        logger.info(f"Reminder: User {user_id} should complete habit '{habit_name}' (ID: {habit_id}) at {reminder_time}")
        
        # Example: Send email
        # email_service.send_reminder(user_email, habit_name, reminder_time)
        
        # Example: Send push notification
        # push_service.send_notification(user_id, f"Don't forget: {habit_name}")
        
    except Exception as e:
        logger.error(f"Error sending reminder: {e}")


def check_and_send_reminders():
    """Check for habits that need reminders and send them"""
    db = SessionLocal()
    try:
        from app.habits.models import Habit
        
        # Get current time
        now = datetime.now()
        current_time = now.strftime("%H:%M")
        today = date.today()
        
        # Get all active habits with reminders enabled
        habits = db.query(Habit).filter(
            Habit.is_active == True,
            Habit.reminder_time.isnot(None)
        ).all()
        
        for habit in habits:
            # Check if reminder time matches current time (within 1 minute window)
            reminder_time = habit.reminder_time
            if reminder_time:
                # Parse reminder time
                try:
                    reminder_hour, reminder_minute = map(int, reminder_time.split(":"))
                    reminder_datetime = datetime.now().replace(hour=reminder_hour, minute=reminder_minute, second=0, microsecond=0)
                    
                    # Check if it's time to send reminder (within 1 minute)
                    time_diff = abs((now - reminder_datetime).total_seconds())
                    if time_diff <= 60:  # Within 1 minute
                        # Check user preferences
                        user_pref = db.query(UserPreference).filter(
                            UserPreference.user_id == habit.user_id
                        ).first()
                        
                        if user_pref and user_pref.reminder_enabled:
                            # Check if habit is already completed today
                            completion_repo = HabitCompletionRepository(db)
                            today_completion = completion_repo.get_by_date(
                                habit.user_id,
                                habit.id,
                                today
                            )
                            
                            if not today_completion:
                                # Send reminder
                                send_reminder(
                                    habit.user_id,
                                    habit.id,
                                    habit.name,
                                    reminder_time
                                )
                                logger.info(f"Sent reminder for habit {habit.id} to user {habit.user_id}")
                
                except ValueError:
                    logger.warning(f"Invalid reminder time format for habit {habit.id}: {reminder_time}")
        
    except Exception as e:
        logger.error(f"Error in check_and_send_reminders: {e}")
    finally:
        db.close()


def start_reminder_scheduler():
    """Start the reminder scheduler"""
    scheduler = BackgroundScheduler()
    
    # Run every minute to check for reminders
    scheduler.add_job(
        check_and_send_reminders,
        trigger=CronTrigger(minute="*"),  # Run every minute
        id='reminder_scheduler',
        name='Check and send habit reminders',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Reminder scheduler started")

