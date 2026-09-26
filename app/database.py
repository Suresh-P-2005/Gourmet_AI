"""
Async PostgreSQL database setup using asyncpg.
Creates the recipes table on startup.
"""

import asyncpg
from app.core.config import get_settings


async def get_db() -> asyncpg.Connection:
    """Get an async database connection."""
    settings = get_settings()
    # asyncpg can accept the URL directly
    conn = await asyncpg.connect(settings.DATABASE_URL)
    return conn


async def init_db() -> None:
    """Initialize the database and create tables if they don't exist."""
    settings = get_settings()
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                cuisine TEXT DEFAULT '',
                dietary TEXT DEFAULT '',
                ingredients TEXT NOT NULL,
                instructions TEXT NOT NULL,
                notes TEXT DEFAULT '',
                nutrition TEXT DEFAULT '{}',
                suggestions TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    finally:
        await conn.close()
