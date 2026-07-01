"""
Security utilities — simple in-memory rate limiter and input sanitization.
"""

import time
from collections import defaultdict
from fastapi import HTTPException, Request


class RateLimiter:
    """
    Simple in-memory sliding-window rate limiter.
    Tracks requests per IP address within a time window.
    """

    def __init__(self, max_requests: int = 30, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._requests: dict[str, list[float]] = defaultdict(list)

    def check(self, client_ip: str) -> None:
        """Raise 429 if the client has exceeded the rate limit."""
        now = time.time()
        cutoff = now - self.window_seconds

        # Prune old timestamps
        self._requests[client_ip] = [
            ts for ts in self._requests[client_ip] if ts > cutoff
        ]

        if len(self._requests[client_ip]) >= self.max_requests:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please slow down and try again shortly.",
            )

        self._requests[client_ip].append(now)


# Global rate limiter instance
rate_limiter = RateLimiter()


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """Strip dangerous characters and enforce length limits."""
    if not text:
        return ""
    # Truncate to max length
    text = text[:max_length].strip()
    return text
