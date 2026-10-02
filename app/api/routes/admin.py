from fastapi import APIRouter, Depends, HTTPException, status
from app.models.response_models import UserResponse
from app.api.routes.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/admin", tags=["Admin"])

async def get_current_admin(current_user: UserResponse = Depends(get_current_user)):
    # Since UserResponse currently might not have is_admin, we need to check it from DB
    async for db in get_db():
        user_row = await db.fetchrow("SELECT is_admin FROM users WHERE username = $1", current_user.username)
        if not user_row or not user_row['is_admin']:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions. Admin access required."
            )
        return current_user

@router.get("/users")
async def get_all_users(admin: UserResponse = Depends(get_current_admin)):
    async for db in get_db():
        users = await db.fetch("""
            SELECT id, username, email, is_verified, auth_provider, is_admin, 
                   (SELECT COUNT(*) FROM recipes WHERE user_id = users.id) as recipe_count
            FROM users 
            ORDER BY id ASC
        """)
        return {"success": True, "users": [dict(u) for u in users]}

@router.delete("/users/{user_id}")
async def delete_user(user_id: int, admin: UserResponse = Depends(get_current_admin)):
    async for db in get_db():
        # Prevent self-deletion
        admin_row = await db.fetchrow("SELECT id FROM users WHERE username = $1", admin.username)
        if admin_row['id'] == user_id:
            raise HTTPException(status_code=400, detail="Cannot delete your own admin account")
            
        result = await db.execute("DELETE FROM users WHERE id = $1", user_id)
        if result == "DELETE 0":
            raise HTTPException(status_code=404, detail="User not found")
            
        return {"success": True, "message": "User deleted successfully"}

@router.put("/users/{user_id}/toggle-admin")
async def toggle_admin(user_id: int, admin: UserResponse = Depends(get_current_admin)):
    async for db in get_db():
        admin_row = await db.fetchrow("SELECT id FROM users WHERE username = $1", admin.username)
        if admin_row['id'] == user_id:
            raise HTTPException(status_code=400, detail="Cannot modify your own admin status")
            
        # Get current status
        user = await db.fetchrow("SELECT is_admin FROM users WHERE id = $1", user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        new_status = not user['is_admin']
        await db.execute("UPDATE users SET is_admin = $1 WHERE id = $2", new_status, user_id)
        
        return {"success": True, "is_admin": new_status, "message": f"User admin status changed to {new_status}"}
