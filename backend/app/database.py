from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from app.config import settings
import logging
import time

logger = logging.getLogger(__name__)

# Log the DATABASE_URL (masking password for security)
def mask_password(url: str) -> str:
    """Mask password in database URL for logging"""
    try:
        if '@' in url:
            parts = url.split('@')
            if ':' in parts[0]:
                user_pass = parts[0].split('://')[1] if '://' in parts[0] else parts[0]
                if ':' in user_pass:
                    user, _ = user_pass.split(':', 1)
                    return url.replace(user_pass, f"{user}:***")
    except Exception:
        pass
    return url

logger.info(f"Initializing database connection: {mask_password(settings.DATABASE_URL)}")

# Create engine with connection retry logic
def create_db_engine_with_retry(max_retries=30, retry_delay=1):
    """Create database engine with retry logic for startup"""
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args={"connect_timeout": 5}
            )
            # Test the connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Database engine created and connection verified successfully")
            return engine
        except (OperationalError, Exception) as e:
            if attempt < max_retries - 1:
                logger.warning(f"Database connection attempt {attempt + 1}/{max_retries} failed: {e}. Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"Failed to create database engine after {max_retries} attempts: {e}")
                logger.error(f"DATABASE_URL value: {mask_password(settings.DATABASE_URL)}")
                raise

try:
    engine = create_db_engine_with_retry()
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    logger.error(f"DATABASE_URL value: {mask_password(settings.DATABASE_URL)}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection():
    """Check if database connection is working"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

