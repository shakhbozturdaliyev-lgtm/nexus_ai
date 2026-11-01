"""In-memory token bucket rate limiting utilities."""

import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import HTTPException, Request, status
from backend.app.core.logging import logger


class TokenBucketLimiter:
    """Token bucket rate limiter tracking requests per key."""

    def __init__(self, rate_per_minute: int = 60, burst_limit: int = 15):
        self.rate_per_second = rate_per_minute / 60.0
        self.capacity = burst_limit
        # {key: (tokens, last_updated_time)}
        self.buckets: Dict[str, Tuple[float, float]] = defaultdict(lambda: (self.capacity, time.time()))

    def is_allowed(self, key: str) -> bool:
        """Check and consume a token if available."""
        now = time.time()
        tokens, last_time = self.buckets[key]

        # Replenish tokens based on elapsed time
        elapsed = now - last_time
        tokens = min(self.capacity, tokens + (elapsed * self.rate_per_second))

        if tokens >= 1.0:
            self.buckets[key] = (tokens - 1.0, now)
            return True

        self.buckets[key] = (tokens, now)
        return False


# Global limiters
api_limiter = TokenBucketLimiter(rate_per_minute=120, burst_limit=30)
telegram_user_limiter = TokenBucketLimiter(rate_per_minute=20, burst_limit=5)


async def rate_limit_dependency(request: Request):
    """FastAPI dependency to throttle requests based on client host IP."""
    client_ip = request.client.host if request.client else "unknown"
    if not api_limiter.is_allowed(client_ip):
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait a few seconds before trying again.",
        )
