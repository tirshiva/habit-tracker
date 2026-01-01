import redis
from app.config import settings
import json
from typing import Optional, Any

redis_client = redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5
)


def get_cache(key: str) -> Optional[Any]:
    """Get value from cache"""
    try:
        value = redis_client.get(key)
        if value:
            return json.loads(value)
        return None
    except Exception as e:
        print(f"Cache get error: {e}")
        return None


def set_cache(key: str, value: Any, expire: int = 3600) -> bool:
    """Set value in cache with expiration"""
    try:
        redis_client.setex(
            key,
            expire,
            json.dumps(value, default=str)
        )
        return True
    except Exception as e:
        print(f"Cache set error: {e}")
        return False


def delete_cache(key: str) -> bool:
    """Delete value from cache"""
    try:
        redis_client.delete(key)
        return True
    except Exception as e:
        print(f"Cache delete error: {e}")
        return False


def delete_cache_pattern(pattern: str) -> int:
    """Delete all keys matching pattern"""
    try:
        keys = redis_client.keys(pattern)
        if keys:
            return redis_client.delete(*keys)
        return 0
    except Exception as e:
        print(f"Cache delete pattern error: {e}")
        return 0

