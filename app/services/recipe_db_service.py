"""
Recipe Database Service — CRUD operations for saved recipes using PostgreSQL.
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
        recipe_id = await db.fetchval(
            """
            INSERT INTO recipes (title, cuisine, dietary, ingredients, instructions, notes, nutrition, suggestions)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
            """,
            recipe_data.get("title", "Untitled Recipe"),
            recipe_data.get("cuisine", ""),
            recipe_data.get("dietary", ""),
            json.dumps(recipe_data.get("ingredients", [])),
            json.dumps(recipe_data.get("instructions", [])),
            recipe_data.get("notes", ""),
            json.dumps(recipe_data.get("nutrition", {})),
            recipe_data.get("suggestions", ""),
        )
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
        total = await db.fetchval("SELECT COUNT(*) FROM recipes")

        # Get paginated recipes
        rows = await db.fetch(
            "SELECT * FROM recipes ORDER BY created_at DESC LIMIT $1 OFFSET $2",
            limit, offset,
        )

        recipes = []
        for row in rows:
            recipes.append({
                "id": row["id"],
                "title": row["title"],
                "cuisine": row["cuisine"] or "",
                "dietary": row["dietary"] or "",
                "ingredients": json.loads(row["ingredients"]) if row["ingredients"] else [],
                "instructions": json.loads(row["instructions"]) if row["instructions"] else [],
                "notes": row["notes"] or "",
                "nutrition": json.loads(row["nutrition"]) if row["nutrition"] else {},
                "suggestions": row["suggestions"] or "",
                "created_at": str(row["created_at"]) if row["created_at"] else "",
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
        result = await db.execute("DELETE FROM recipes WHERE id = $1", recipe_id)
        deleted = result.startswith("DELETE ") and int(result.split()[1]) > 0
        if deleted:
            logger.info(f"Recipe {recipe_id} deleted")
        return deleted
    finally:
        await db.close()
