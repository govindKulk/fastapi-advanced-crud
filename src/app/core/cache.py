import json
from redis.asyncio import Redis, from_url  # type: ignore[attr-defined]
from typing import Any, Optional
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url: str = redis_url
        self.redis_client: Optional[Redis[str]] = None  # type: ignore[type-arg]

    async def connect(self) -> None:
        """Connect to Redis"""
        logger.info(f"Attempting to connect to Redis at {self.redis_url}")
        
        try:
            self.redis_client = from_url(  # type: ignore[assignment]
                url=self.redis_url,
                encoding="utf8",
                decode_responses=True
            )
            await self.redis_client.ping()  # type: ignore[misc]
            logger.info("✅ Connected to Redis successfully")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            logger.warning("Cache will be disabled - continuing without Redis")
            self.redis_client = None

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()  # type: ignore[misc]

    async def get(self, key: str) -> Any:
        """Get value from cache"""
        if not self.redis_client:
            return None

        try:
            value = await self.redis_client.get(key)  # type: ignore[misc]
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        if not self.redis_client:
            return False

        try:
            json_value = json.dumps(value, default=str)
            await self.redis_client.setex(key, ttl, json_value)  # type: ignore[misc]
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        if not self.redis_client:
            return False

        try:
            await self.redis_client.delete(key)  # type: ignore[misc]
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern"""
        if not self.redis_client:
            return 0

        try:
            keys = await self.redis_client.keys(pattern)  # type: ignore[misc]
            if keys:
                return await self.redis_client.delete(*keys)  # type: ignore[misc]
        except Exception as e:
            logger.error(f"Cache clear pattern error for {pattern}: {e}")
        return 0

# Global cache manager instance
cache_manager = CacheManager(
    redis_url= settings.REDIS_URL
    
)