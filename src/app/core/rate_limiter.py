import time
import logging
from fastapi import HTTPException, Request, status
from app.core.cache import cache_manager

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int):
        logger.info("۞ Initializing RateLimiter... ")
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def is_allowed(self, identifier: str) -> bool:
        """Check if request is allowed using fixed window"""
        current_time = int(time.time())
        # Use fixed window start based on window_seconds intervals
        # This ensures the same window_start for all requests within the same time window
        window_start = (current_time // self.window_seconds) * self.window_seconds

        # Generate consistent key for the current time window
        key = f"rate_limit:{identifier}:{window_start}"
        logger.info(f"🔑 Rate limit key: {key}")
        
        # Get current request count for this window
        count_data = await cache_manager.get(key)
        current_count = count_data if isinstance(count_data, int) else 0
        
        logger.info(f"📊 Current count: {current_count}/{self.max_requests} for {identifier}")

        if current_count >= self.max_requests:
            logger.warning(f"🚫 Rate limit exceeded for {identifier}")
            return False

        # Increment counter with TTL to auto-expire
        new_count = current_count + 1
        await cache_manager.set(key, new_count, self.window_seconds)
        logger.info(f"✅ Request allowed ({new_count}/{self.max_requests}) for {identifier}")
        return True

    async def __call__(self, request: Request) -> None:
        """Rate limiting dependency"""
        # Use IP address as identifier (in production, use user ID)
        identifier = request.client.host if request.client else "unknown"

        if not await self.is_allowed(identifier):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later."
            )

# Rate limiters for different endpoints
rate_limiter_strict = RateLimiter(max_requests=10, window_seconds=60)  # 10 requests per minute
rate_limiter_moderate = RateLimiter(max_requests=60, window_seconds=60)  # 60 requests per minute