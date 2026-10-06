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
    async for db in get_db():
        async with db.transaction():
            recipe_id = await db.fetchval(
                """
                INSERT INTO recipes (
                    user_id, title, cuisine, cuisine_type, dietary, language,
                    ingredients, instructions, notes, personal_notes, 
                    is_public, nutrition, suggestions
                )
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id
                """,
                user_id,
                recipe_data.get("title", "Untitled Recipe"),
                recipe_data.get("cuisine", ""),
                recipe_data.get("cuisine_type", "Other"),
                recipe_data.get("dietary", ""),
                recipe_data.get("language", "English"),
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

def _format_recipe_row(row):
    def parse_jsonb(val):
        if not val:
            return None
        if isinstance(val, str):
            try:
                return json.loads(val)
            except:
                return val
        return val

    return {
        "id": row["id"],
        "title": row["title"],
        "cuisine": row["cuisine"] or "",
        "cuisine_type": row["cuisine_type"] or "Other",
        "dietary": row["dietary"] or "",
        "language": row.get("language") or "English",
        "ingredients": parse_jsonb(row["ingredients"]) or [],
        "instructions": parse_jsonb(row["instructions"]) or [],
        "notes": row["notes"] or "",
        "personal_notes": row["personal_notes"] or "",
        "is_public": row.get("is_public", False),
        "nutrition": parse_jsonb(row["nutrition"]) or {},
        "suggestions": row["suggestions"] or "",
        "created_at": str(row["created_at"]) if row["created_at"] else "",
    }

import base64

def _encode_cursor(data: dict) -> str:
    return base64.b64encode(json.dumps(data).encode('utf-8')).decode('utf-8')

def _decode_cursor(cursor: str) -> dict:
    if not cursor:
        return {}
    try:
        return json.loads(base64.b64decode(cursor).decode('utf-8'))
    except Exception:
        return {}

async def get_user_vault_recipes(user_id: int, limit: int = 20, cursor: str = None) -> tuple[list[dict], int, Optional[str]]:
    """Get saved recipes for a specific user using cursor pagination."""
    async for db in get_db():
        cursor_data = _decode_cursor(cursor)
        last_created_at = cursor_data.get('created_at')
        last_id = cursor_data.get('id')
        
        query = "SELECT *, count(*) over() as total_count FROM recipes WHERE user_id = $1"
        args = [user_id]
        
        if last_created_at and last_id:
            args.extend([last_created_at, last_id])
            query += f" AND (created_at, id) < (${len(args)-1}::timestamp, ${len(args)})"
            
        args.append(limit)
        query += f" ORDER BY created_at DESC, id DESC LIMIT ${len(args)}"
        
        rows = await db.fetch(query, *args)
        total = rows[0]['total_count'] if rows else 0
        recipes = [_format_recipe_row(row) for row in rows]
        
        next_cursor = None
        if len(recipes) == limit:
            last_recipe = rows[-1]
            next_cursor = _encode_cursor({
                'created_at': str(last_recipe['created_at']),
                'id': last_recipe['id']
            })
            
        return recipes, total, next_cursor

async def get_community_recipes(limit: int = 20, cursor: str = None, cuisine_type: str = None, search: str = None) -> tuple[list[dict], int, Optional[str]]:
    """Get public community recipes using cursor pagination (or offset for search)."""
    async for db in get_db():
        cursor_data = _decode_cursor(cursor)
        query = "SELECT *, count(*) over() as total_count FROM recipes WHERE is_public = TRUE"
        args = []
        
        if cuisine_type and cuisine_type != 'All':
            args.append(cuisine_type)
            query += f" AND cuisine_type = ${len(args)}"
            
        if search:
            # Fallback to offset pagination for full-text search
            offset = cursor_data.get('offset', 0)
            search_terms = ' & '.join([word + ':*' for word in search.split() if word.isalnum()])
            if search_terms:
                args.append(search_terms)
                query += f" AND search_vector @@ to_tsquery('english', ${len(args)})"
                query = query.replace("SELECT *", f"SELECT *, ts_rank(search_vector, to_tsquery('english', ${len(args)})) as rank")
            
            args.extend([limit, offset])
            if 'rank' in query:
                query += f" ORDER BY rank DESC, created_at DESC, id DESC LIMIT ${len(args)-1} OFFSET ${len(args)}"
            else:
                query += f" ORDER BY created_at DESC, id DESC LIMIT ${len(args)-1} OFFSET ${len(args)}"
                
            rows = await db.fetch(query, *args)
            total = rows[0]['total_count'] if rows else 0
            recipes = [_format_recipe_row(row) for row in rows]
            
            next_cursor = None
            if len(recipes) == limit:
                next_cursor = _encode_cursor({'offset': offset + limit})
                
            return recipes, total, next_cursor
            
        else:
            # High-speed cursor pagination for normal browsing
            last_created_at = cursor_data.get('created_at')
            last_id = cursor_data.get('id')
            
            if last_created_at and last_id:
                args.extend([last_created_at, last_id])
                query += f" AND (created_at, id) < (${len(args)-1}::timestamp, ${len(args)})"
                
            args.append(limit)
            query += f" ORDER BY created_at DESC, id DESC LIMIT ${len(args)}"
            
            rows = await db.fetch(query, *args)
            total = rows[0]['total_count'] if rows else 0
            recipes = [_format_recipe_row(row) for row in rows]
            
            next_cursor = None
            if len(recipes) == limit:
                last_recipe = rows[-1]
                next_cursor = _encode_cursor({
                    'created_at': str(last_recipe['created_at']),
                    'id': last_recipe['id']
                })
                
            return recipes, total, next_cursor

async def delete_recipe(recipe_id: int, user_id: int) -> bool:
    """Delete a recipe by ID, ensuring user ownership."""
    async for db in get_db():
        async with db.transaction():
            result = await db.execute("DELETE FROM recipes WHERE id = $1 AND user_id = $2", recipe_id, user_id)
            deleted = result.startswith("DELETE ") and int(result.split()[1]) > 0
            if deleted:
                logger.info(f"Recipe {recipe_id} deleted by {user_id}")
            return deleted

async def toggle_recipe_visibility(recipe_id: int, user_id: int, is_public: bool) -> bool:
    """Toggle the is_public flag."""
    async for db in get_db():
        async with db.transaction():
            result = await db.execute("UPDATE recipes SET is_public = $1 WHERE id = $2 AND user_id = $3", is_public, recipe_id, user_id)
            updated = result.startswith("UPDATE ") and int(result.split()[1]) > 0
            return updated

async def bookmark_recipe(recipe_id: int, user_id: int) -> bool:
    """Save a community recipe to user's saved_recipes."""
    async for db in get_db():
        async with db.transaction():
            # Ensure it is public or belongs to user
            recipe = await db.fetchrow("SELECT id FROM recipes WHERE id = $1 AND (is_public = TRUE OR user_id = $2)", recipe_id, user_id)
            if not recipe:
                return False
                
            try:
                await db.execute("INSERT INTO saved_recipes (user_id, recipe_id) VALUES ($1, $2)", user_id, recipe_id)
                return True
            except asyncpg.exceptions.UniqueViolationError:
                return True # already bookmarked
