from pydantic_settings import BaseSettings
from pydantic import model_validator
from typing import Optional
from urllib.parse import quote_plus, urlparse
import os


class Settings(BaseSettings):
    # Database
    DATABASE_URL: Optional[str] = None
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "habit_tracker"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # JWT
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    # Sentry
    SENTRY_DSN: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Application
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @model_validator(mode='after')
    def validate_database_url(self):
        """Validate and fix DATABASE_URL if needed"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Always reconstruct from components to ensure it's correct
        # This is safer than trying to parse and fix malformed URLs
        encoded_password = quote_plus(str(self.POSTGRES_PASSWORD))
        encoded_user = quote_plus(str(self.POSTGRES_USER))
        reconstructed_url = f"postgresql://{encoded_user}:{encoded_password}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        
        # Always use reconstructed URL to avoid any malformed URL issues
        # The environment variable might be incorrectly formatted
        original_url = self.DATABASE_URL
        self.DATABASE_URL = reconstructed_url
        
        if original_url and original_url != reconstructed_url:
            # Mask password in original URL for logging
            masked_original = original_url
            try:
                if '@' in original_url:
                    parts = original_url.split('@')
                    if '://' in parts[0]:
                        user_pass = parts[0].split('://')[1]
                        if ':' in user_pass:
                            user, _ = user_pass.split(':', 1)
                            masked_original = original_url.replace(user_pass, f"{user}:***")
            except Exception:
                pass
            logger.warning(f"DATABASE_URL was reconstructed. Original (masked): {masked_original[:80]}")
        
        logger.info(f"Using DATABASE_URL: postgresql://{encoded_user}:***@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}")
        return self


settings = Settings()

