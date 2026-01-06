"""
Rate limiter for Polymarket API requests.
"""

import asyncio
import time
from enum import Enum
from typing import Dict


class EndpointCategory(Enum):
    """API endpoint categories with different rate limits."""
    
    GAMMA_API = "gamma"      # Market discovery - 10 req/sec
    CLOB_API = "clob"        # Orderbook/trading - 5 req/sec
    PRICE_HISTORY = "prices" # Price data - 5 req/sec


# Rate limits per category (requests per second)
RATE_LIMITS: Dict[EndpointCategory, float] = {
    EndpointCategory.GAMMA_API: 10.0,
    EndpointCategory.CLOB_API: 5.0,
    EndpointCategory.PRICE_HISTORY: 5.0,
}


class RateLimiter:
    """
    Token bucket rate limiter for API requests.
    """
    
    def __init__(self):
        self._last_request: Dict[EndpointCategory, float] = {}
        self._locks: Dict[EndpointCategory, asyncio.Lock] = {
            cat: asyncio.Lock() for cat in EndpointCategory
        }
    
    async def acquire(self, category: EndpointCategory) -> None:
        """
        Wait until a request can be made to the given endpoint category.
        
        Args:
            category: The endpoint category to rate limit
        """
        async with self._locks[category]:
            min_interval = 1.0 / RATE_LIMITS[category]
            
            last = self._last_request.get(category, 0)
            elapsed = time.time() - last
            
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            
            self._last_request[category] = time.time()


# Global rate limiter instance
_rate_limiter: RateLimiter | None = None


def get_rate_limiter() -> RateLimiter:
    """Get or create the global rate limiter."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter
