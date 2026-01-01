from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.database import get_db
from app.auth.service import AuthService
from app.auth.schemas import UserCreate, UserLogin, Token, UserResponse
from app.shared.dependencies import get_current_user
from app.shared.rate_limiter import get_rate_limiter

router = APIRouter()
limiter = get_rate_limiter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def register(
    user_data: UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    try:
        auth_service = AuthService(db)
        user_dict = auth_service.register(user_data)
        return user_dict
    except HTTPException:
        # Re-raise HTTP exceptions (like email/username already exists)
        raise
    except Exception as e:
        # Log unexpected errors and return a user-friendly message
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    auth_service = AuthService(db)
    credentials = UserLogin(username=form_data.username, password=form_data.password)
    return auth_service.login(credentials)


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user information"""
    auth_service = AuthService(db)
    user_info = auth_service.get_current_user_info(current_user.id)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user_info

