from sqlalchemy.orm import Session
from app.auth.models import User
from app.preferences.models import UserPreference
from typing import Optional


class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()
    
    def create(self, user_data: dict) -> User:
        """Create a new user"""
        user = User(**user_data)
        self.db.add(user)
        self.db.flush()
        
        # Create default preferences
        preferences = UserPreference(user_id=user.id)
        self.db.add(preferences)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update(self, user: User, user_data: dict) -> User:
        """Update user"""
        for key, value in user_data.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def delete(self, user: User) -> bool:
        """Delete user"""
        self.db.delete(user)
        self.db.commit()
        return True

