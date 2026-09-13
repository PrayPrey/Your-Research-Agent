"""Rate limiter for API calls using token bucket algorithm."""
import time
from typing import List


class RateLimiter:
    """Token bucket rate limiter for API calls."""

    def __init__(self, max_calls: int, period: int):
        """Initialize rate limiter.

        Args:
            max_calls: Maximum number of calls allowed in the period
            period: Time period in seconds
        """
        self.max_calls = max_calls
        self.period = period
        self.calls: List[float] = []

    def wait_if_needed(self):
        """Block if rate limit would be exceeded."""
        now = time.time()
        self.calls = [t for t in self.calls if now - t < self.period]

        if len(self.calls) >= self.max_calls:
            sleep_time = self.period - (now - self.calls[0])
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.calls.append(now)
