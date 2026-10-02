from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.models.response_models import UserResponse
from app.api.routes.auth import get_current_user
from app.database import get_db
import datetime

router = APIRouter(prefix="/api/user", tags=["User"])

class AvatarUpload(BaseModel):
    avatar_base64: str

@router.get("/profile")
async def get_profile(current_user: UserResponse = Depends(get_current_user)):
    async for db in get_db():
        user_row = await db.fetchrow(
            """
            SELECT id, username, email, is_admin, avatar
            FROM users 
            WHERE id = $1
            """,
            current_user.id
        )
        if not user_row:
            raise HTTPException(status_code=404, detail="User not found")
            
        stats_row = await db.fetchrow(
            """
            SELECT 
                (SELECT COUNT(*) FROM recipes WHERE user_id = $1) as total_recipes,
                (SELECT COUNT(*) FROM recipes WHERE user_id = $1 AND is_public = true) as public_recipes
            """,
            current_user.id
        )
        
        return {
            "success": True,
            "user": {
                "username": user_row['username'],
                "email": user_row['email'],
                "is_admin": user_row['is_admin'],
                "avatar": user_row['avatar']
            },
            "stats": {
                "total_generated": stats_row['total_recipes'] or 0,
                "total_saved": stats_row['total_recipes'] or 0 # All generated recipes are saved
            }
        }

@router.post("/avatar")
async def update_avatar(data: AvatarUpload, current_user: UserResponse = Depends(get_current_user)):
    try:
        async for db in get_db():
            # We assume data.avatar_base64 contains the data URL
            await db.execute("UPDATE users SET avatar = $1 WHERE id = $2", data.avatar_base64, current_user.id)
            return {"success": True, "message": "Avatar updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
