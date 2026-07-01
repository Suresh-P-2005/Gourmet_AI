"""
Async SQLite database setup using aiosqlite.
Creates the recipes table on startup.
"""

import aiosqlite
import os

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "recipes.db")


async def get_db() -> aiosqlite.Connection:
    """Get an async database connection."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    return db


async def init_db() -> None:
    """Initialize the database and create tables if they don't exist."""
    db = await aiosqlite.connect(DATABASE_PATH)
    try:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS recipes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        await db.commit()
    finally:
        await db.close()
