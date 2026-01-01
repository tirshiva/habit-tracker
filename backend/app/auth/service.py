from sqlalchemy.orm import Session
from datetime import timedelta
from app.auth.repository import UserRepository
from app.auth.schemas import UserCreate, UserLogin
from app.shared.security import verify_password, get_password_hash, create_access_token
from app.config import settings
from app.redis_client import set_cache, get_cache, delete_cache
from fastapi import HTTPException, status
from typing import Optional


class AuthService:
    def __init__(self, db: Session):
        self.user_repo = UserRepository(db)
        self.db = db
    
    def register(self, user_data: UserCreate) -> dict:
        """Register a new user"""
        # Check if user already exists
        if self.user_repo.get_by_email(user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if self.user_repo.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Create user
        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = get_password_hash(user_data.password)
        del user_dict["password"]
        
        user = self.user_repo.create(user_dict)
        
        # Invalidate cache
        delete_cache(f"user:{user.id}")
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name
        }
    
    def login(self, credentials: UserLogin) -> dict:
        """Authenticate user and return token"""
        user = self.user_repo.get_by_username(credentials.username)
        
        if not user or not verify_password(credentials.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=access_token_expires
        )
        
        # Cache user data
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name
        }
        set_cache(f"user:{user.id}", user_data, expire=1800)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_data
        }
    
    def get_current_user_info(self, user_id: int) -> Optional[dict]:
        """Get current user information with caching"""
        # Try cache first
        cache_key = f"user:{user_id}"
        cached_user = get_cache(cache_key)
        if cached_user:
            return cached_user
        
        # Get from database
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        user_data = {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "created_at": user.created_at.isoformat()
        }
        
        # Cache for 30 minutes
        set_cache(cache_key, user_data, expire=1800)
        return user_data

