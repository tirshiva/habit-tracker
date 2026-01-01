from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response schema"""
    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseResponse):
    """Error response schema"""
    success: bool = False
    error: str

