"""
Redis Cache Manager
"""

from typing import Optional
import json


class RedisCache:
    """
    Redis-based caching for query results
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        """
        Initialize Redis client
        
        Args:
            redis_url: Redis connection URL
        """
        self.redis_url = redis_url
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Redis client"""
        try:
            import redis
            self.client = redis.from_url(self.redis_url, decode_responses=True)
            self.client.ping()
            print(f"✅ Connected to Redis")
        except ImportError:
            print("⚠️  redis package not installed. Caching unavailable.")
        except Exception as e:
            print(f"⚠️  Could not connect to Redis: {e}")
    
    async def get(self, key: str) -> Optional[str]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.client:
            return None
        
        try:
            return self.client.get(key)
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: str, expire: int = 3600):
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache
            expire: Expiration time in seconds
        """
        if not self.client:
            return
        
        try:
            self.client.setex(key, expire, value)
        except Exception as e:
            print(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.client:
            return
        
        try:
            self.client.delete(key)
        except Exception as e:
            print(f"Cache delete error: {e}")
