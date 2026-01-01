from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from app.config import settings
import hashlib
import bcrypt
import base64


def _pre_hash_password(password: str) -> bytes:
    """
    Pre-hash password with SHA-256 to handle bcrypt's 72-byte limit.
    This allows passwords longer than 72 bytes while maintaining security.
    Returns bytes (32 bytes) which is well under bcrypt's 72-byte limit.
    """
    return hashlib.sha256(password.encode('utf-8')).digest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    try:
        # Pre-hash the plain password before verification to match the stored hash
        pre_hashed = _pre_hash_password(plain_password)
        # bcrypt.checkpw expects bytes
        return bcrypt.checkpw(pre_hashed, hashed_password.encode('utf-8'))
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    Pre-hashes with SHA-256 first to handle passwords longer than 72 bytes.
    Returns the hash as a string (bcrypt format).
    """
    # Pre-hash with SHA-256 to handle bcrypt's 72-byte limit
    # This gives us 32 bytes, well under the 72-byte limit
    pre_hashed = _pre_hash_password(password)
    # Generate bcrypt hash (returns bytes)
    hashed = bcrypt.hashpw(pre_hashed, bcrypt.gensalt())
    # Return as string for storage
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

