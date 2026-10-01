from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.request_models import UserCreateRequest
from app.models.response_models import Token, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import get_settings
from app.database import get_db
from jose import JWTError, jwt
import asyncpg

router = APIRouter(prefix="/api/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    db = await get_db()
    try:
        user_row = await db.fetchrow("SELECT id, username, email FROM users WHERE username = $1", username)
        if user_row is None:
            raise credentials_exception
        return UserResponse(**dict(user_row))
    finally:
        await db.close()

@router.post("/signup", response_model=UserResponse)
async def create_user(user: UserCreateRequest):
    db = await get_db()
    try:
        hashed_password = get_password_hash(user.password)
        try:
            row = await db.fetchrow(
                "INSERT INTO users (username, email, hashed_password) VALUES ($1, $2, $3) RETURNING id, username, email",
                user.username, user.email, hashed_password
            )
            return UserResponse(**dict(row))
        except asyncpg.exceptions.UniqueViolationError as e:
            raise HTTPException(status_code=400, detail="Username or email already registered")
    finally:
        await db.close()

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = await get_db()
    try:
        user_row = await db.fetchrow("SELECT * FROM users WHERE username = $1", form_data.username)
        if not user_row or not verify_password(form_data.password, user_row['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token = create_access_token(data={"sub": user_row['username']})
        return {"access_token": access_token, "token_type": "bearer"}
    finally:
        await db.close()

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user
