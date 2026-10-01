"""
Recipe Database Service — CRUD operations for saved recipes using PostgreSQL.
"""

import json
import logging
from typing import Optional

import asyncpg
from app.database import get_db

logger = logging.getLogger(__name__)


async def save_recipe(recipe_data: dict, user_id: int) -> int:
    """
    Save a recipe to the database.
    """
    db = await get_db()
    try:
        async with db._conn.transaction():
            recipe_id = await db.fetchval(
                """
                INSERT INTO recipes (
                    user_id, title, cuisine, cuisine_type, dietary, 
                    ingredients, instructions, notes, personal_notes, 
                    is_public, nutrition, suggestions
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                RETURNING id
                """,
                user_id,
                recipe_data.get("title", "Untitled Recipe"),
                recipe_data.get("cuisine", ""),
                recipe_data.get("cuisine_type", "Other"),
                recipe_data.get("dietary", ""),
                json.dumps(recipe_data.get("ingredients", [])),
                json.dumps(recipe_data.get("instructions", [])),
                recipe_data.get("notes", ""),
                recipe_data.get("personal_notes", ""),
                recipe_data.get("is_public", False),
                json.dumps(recipe_data.get("nutrition", {})),
                recipe_data.get("suggestions", ""),
            )
            logger.info(f"Recipe saved with ID: {recipe_id} for User {user_id}")
            return recipe_id
    finally:
        await db.close()

def _format_recipe_row(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "cuisine": row["cuisine"] or "",
        "cuisine_type": row["cuisine_type"] or "Other",
        "dietary": row["dietary"] or "",
        "ingredients": json.loads(row["ingredients"]) if row["ingredients"] else [],
        "instructions": json.loads(row["instructions"]) if row["instructions"] else [],
        "notes": row["notes"] or "",
        "personal_notes": row["personal_notes"] or "",
        "is_public": row.get("is_public", False),
        "nutrition": json.loads(row["nutrition"]) if row["nutrition"] else {},
        "suggestions": row["suggestions"] or "",
        "created_at": str(row["created_at"]) if row["created_at"] else "",
    }

async def get_user_vault_recipes(user_id: int, limit: int = 20, offset: int = 0) -> tuple[list[dict], int]:
    """Get saved recipes for a specific user."""
    db = await get_db()
    try:
        total = await db.fetchval("SELECT COUNT(*) FROM recipes WHERE user_id = $1", user_id)
        rows = await db.fetch(
            "SELECT * FROM recipes WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2 OFFSET $3",
            user_id, limit, offset,
        )
        recipes = [_format_recipe_row(row) for row in rows]
        return recipes, total
    finally:
        await db.close()

async def get_community_recipes(limit: int = 20, offset: int = 0, cuisine_type: str = None, search: str = None) -> tuple[list[dict], int]:
    """Get public community recipes."""
    db = await get_db()
    try:
        query = "SELECT * FROM recipes WHERE is_public = TRUE"
        count_query = "SELECT COUNT(*) FROM recipes WHERE is_public = TRUE"
        args = []
        
        if cuisine_type and cuisine_type != 'All':
            args.append(cuisine_type)
            query += f" AND cuisine_type = ${len(args)}"
            count_query += f" AND cuisine_type = ${len(args)}"
            
        if search:
            search = f"%{search}%"
            args.append(search)
            query += f" AND (title ILIKE ${len(args)} OR ingredients ILIKE ${len(args)})"
            count_query += f" AND (title ILIKE ${len(args)} OR ingredients ILIKE ${len(args)})"
            
        total = await db.fetchval(count_query, *args)
        
        args.append(limit)
        args.append(offset)
        query += f" ORDER BY created_at DESC LIMIT ${len(args)-1} OFFSET ${len(args)}"
        
        rows = await db.fetch(query, *args)
        recipes = [_format_recipe_row(row) for row in rows]
        return recipes, total
    finally:
        await db.close()

async def delete_recipe(recipe_id: int, user_id: int) -> bool:
    """Delete a recipe by ID, ensuring user ownership."""
    db = await get_db()
    try:
        async with db._conn.transaction():
            result = await db.execute("DELETE FROM recipes WHERE id = $1 AND user_id = $2", recipe_id, user_id)
            deleted = result.startswith("DELETE ") and int(result.split()[1]) > 0
            if deleted:
                logger.info(f"Recipe {recipe_id} deleted by {user_id}")
            return deleted
    finally:
        await db.close()

async def toggle_recipe_visibility(recipe_id: int, user_id: int, is_public: bool) -> bool:
    """Toggle the is_public flag."""
    db = await get_db()
    try:
        async with db._conn.transaction():
            result = await db.execute("UPDATE recipes SET is_public = $1 WHERE id = $2 AND user_id = $3", is_public, recipe_id, user_id)
            updated = result.startswith("UPDATE ") and int(result.split()[1]) > 0
            return updated
    finally:
        await db.close()

async def bookmark_recipe(recipe_id: int, user_id: int) -> bool:
    """Save a community recipe to user's saved_recipes."""
    db = await get_db()
    try:
        async with db._conn.transaction():
            # Ensure it is public or belongs to user
            recipe = await db.fetchrow("SELECT id FROM recipes WHERE id = $1 AND (is_public = TRUE OR user_id = $2)", recipe_id, user_id)
            if not recipe:
                return False
                
            try:
                await db.execute("INSERT INTO saved_recipes (user_id, recipe_id) VALUES ($1, $2)", user_id, recipe_id)
                return True
            except asyncpg.exceptions.UniqueViolationError:
                return True # already bookmarked
    finally:
        await db.close()
