"""
Async PostgreSQL database setup using asyncpg with connection pooling.
Configured for production environments like Render.
"""

import ssl
import asyncpg
from typing import Optional
from app.core.config import get_settings

# Global database pool
db_pool: Optional[asyncpg.Pool] = None


async def init_db() -> None:
    """Initialize the database connection pool."""
    global db_pool
    settings = get_settings()

    # Render requires SSL for external connections
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    db_pool = await asyncpg.create_pool(
        settings.DATABASE_URL,
        min_size=1,
        max_size=10,
        ssl=ssl_context
    )


async def close_db() -> None:
    """Close the database connection pool on shutdown."""
    global db_pool
    if db_pool:
        await db_pool.close()
        db_pool = None


class ConnectionWrapper:
    """Wraps an asyncpg connection to release it back to the pool on close()."""
    def __init__(self, pool: asyncpg.Pool, conn: asyncpg.Connection):
        self._pool = pool
        self._conn = conn

    def __getattr__(self, name):
        return getattr(self._conn, name)

    async def close(self):
        """Release the connection back to the pool."""
        await self._pool.release(self._conn)


async def get_db() -> ConnectionWrapper:
    """Acquire a connection from the pool. Caller must call await db.close()."""
    global db_pool
    if not db_pool:
        raise RuntimeError("Database pool is not initialized")
    
    conn = await db_pool.acquire()
    return ConnectionWrapper(db_pool, conn)
