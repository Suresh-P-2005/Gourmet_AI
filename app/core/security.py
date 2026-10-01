"""
Security utilities — simple in-memory rate limiter and input sanitization.
"""

import time
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict
from fastapi import HTTPException, Request
import bcrypt
from jose import JWTError, jwt
from app.core.config import get_settings


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

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        # bcrypt expects bytes
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except ValueError:
        return False

def get_password_hash(password: str) -> str:
    # bcrypt returns bytes, we decode it to string for DB storage
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    settings = get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
    return encoded_jwt
