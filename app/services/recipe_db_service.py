"""
Recipe Database Service — CRUD operations for saved recipes using SQLite.
"""

import json
import logging
from typing import Optional

from app.database import get_db

logger = logging.getLogger(__name__)


async def save_recipe(recipe_data: dict) -> int:
    """
    Save a recipe to the database.
    
    Args:
        recipe_data: Recipe dictionary with title, ingredients, instructions, etc.
    
    Returns:
        The ID of the newly saved recipe
    """
    db = await get_db()
    try:
        cursor = await db.execute(
            """
            INSERT INTO recipes (title, cuisine, dietary, ingredients, instructions, notes, nutrition, suggestions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                recipe_data.get("title", "Untitled Recipe"),
                recipe_data.get("cuisine", ""),
                recipe_data.get("dietary", ""),
                json.dumps(recipe_data.get("ingredients", [])),
                json.dumps(recipe_data.get("instructions", [])),
                recipe_data.get("notes", ""),
                json.dumps(recipe_data.get("nutrition", {})),
                recipe_data.get("suggestions", ""),
            ),
        )
        await db.commit()
        recipe_id = cursor.lastrowid
        logger.info(f"Recipe saved with ID: {recipe_id}")
        return recipe_id
    finally:
        await db.close()


async def get_recipes(limit: int = 20, offset: int = 0) -> tuple[list[dict], int]:
    """
    Get saved recipes with pagination.
    
    Args:
        limit: Max number of recipes to return
        offset: Number of recipes to skip
    
    Returns:
        Tuple of (list of recipe dicts, total count)
    """
    db = await get_db()
    try:
        # Get total count
        cursor = await db.execute("SELECT COUNT(*) FROM recipes")
        row = await cursor.fetchone()
        total = row[0]

        # Get paginated recipes
        cursor = await db.execute(
            "SELECT * FROM recipes ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        )
        rows = await cursor.fetchall()

        recipes = []
        for row in rows:
            recipes.append({
                "id": row[0],
                "title": row[1],
                "cuisine": row[2] or "",
                "dietary": row[3] or "",
                "ingredients": json.loads(row[4]) if row[4] else [],
                "instructions": json.loads(row[5]) if row[5] else [],
                "notes": row[6] or "",
                "nutrition": json.loads(row[7]) if row[7] else {},
                "suggestions": row[8] or "",
                "created_at": str(row[9]) if row[9] else "",
            })

        return recipes, total
    finally:
        await db.close()


async def delete_recipe(recipe_id: int) -> bool:
    """
    Delete a recipe by ID.
    
    Args:
        recipe_id: The database ID of the recipe to delete
    
    Returns:
        True if deleted, False if not found
    """
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
        await db.commit()
        deleted = cursor.rowcount > 0
        if deleted:
            logger.info(f"Recipe {recipe_id} deleted")
        return deleted
    finally:
        await db.close()
