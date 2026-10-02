from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.models.request_models import UserCreateRequest
from app.models.response_models import Token, UserResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import get_settings
from app.database import get_db
from jose import JWTError, jwt
import asyncpg
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.models.request_models import UserCreateRequest, GoogleLoginRequest, VerifyOTPRequest
from app.services.email_service import create_and_send_otp
from datetime import datetime, timezone

router = APIRouter(prefix="/api/auth", tags=["Auth"])

def set_auth_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=True,
        max_age=1800
    )


@router.get("/client-id")
async def get_google_client_id():
    settings = get_settings()
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Client ID not configured")
    return {"client_id": settings.GOOGLE_CLIENT_ID}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(request: Request):
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token = request.cookies.get("access_token")
    if not token:
        # Fallback to header if needed
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            
    if not token:
        raise credentials_exception
        
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        email: str = payload.get("email")
        is_admin: bool = payload.get("is_admin", False)
        if username is None or user_id is None:
            raise credentials_exception
            
        return UserResponse(
            id=user_id,
            username=username,
            email=email,
            is_admin=is_admin
        )
    except JWTError:
        raise credentials_exception

@router.post("/signup")
async def create_user(user: UserCreateRequest):
    async for db in get_db():
        hashed_password = get_password_hash(user.password)
        try:
            is_admin = (user.email.lower() == 'sureshreigns220@gmail.com')
            
            # Create user with is_verified=false
            row = await db.fetchrow(
                "INSERT INTO users (username, email, hashed_password, is_verified, is_admin) VALUES ($1, $2, $3, false, $4) RETURNING id, username, email",
                user.username, user.email, hashed_password, is_admin
            )
            
            # Generate and send OTP
            await create_and_send_otp(row['id'], row['email'])
            
            return {"success": True, "message": "OTP sent to email", "email": row['email']}
        except asyncpg.exceptions.UniqueViolationError as e:
            raise HTTPException(status_code=400, detail="Username or email already registered")

@router.post("/verify-otp", response_model=Token)
async def verify_otp(request: VerifyOTPRequest, response: Response):
    async for db in get_db():
        # Find user
        user = await db.fetchrow("SELECT id, username, is_admin FROM users WHERE email = $1", request.email)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Check OTP
        otp_row = await db.fetchrow(
            "SELECT id, expires_at FROM otps WHERE user_id = $1 AND otp_code = $2 ORDER BY created_at DESC LIMIT 1",
            user['id'], request.otp
        )
        
        if not otp_row:
            raise HTTPException(status_code=400, detail="Invalid OTP")
            
        if otp_row['expires_at'] < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="OTP expired")
            
        # Verify user
        await db.execute("UPDATE users SET is_verified = true WHERE id = $1", user['id'])
        
        # Issue token
        access_token = create_access_token(data={
            "sub": user['username'], 
            "id": user['id'],
            "email": request.email,
            "is_admin": user['is_admin']
        })
        set_auth_cookie(response, access_token)
        return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(response: Response, form_data: OAuth2PasswordRequestForm = Depends()):
    async for db in get_db():
        user_row = await db.fetchrow(
            "SELECT * FROM users WHERE username = $1 OR email = $1", 
            form_data.username
        )
        if not user_row or not verify_password(form_data.password, user_row['hashed_password']):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        if not user_row.get('is_verified', True):
            # Optionally resend OTP here
            await create_and_send_otp(user_row['id'], user_row['email'])
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Email not verified. A new OTP has been sent.",
            )
            
        access_token = create_access_token(data={
            "sub": user_row['username'],
            "id": user_row['id'],
            "email": user_row['email'],
            "is_admin": user_row['is_admin']
        })
        set_auth_cookie(response, access_token)
        return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user

@router.post("/google-login", response_model=Token)
async def google_login(request: GoogleLoginRequest, response: Response):
    settings = get_settings()
    try:
        # Verify the Google token
        id_info = id_token.verify_oauth2_token(
            request.token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )

        email = id_info.get('email')
        google_id = id_info.get('sub')
        name = id_info.get('name')
        picture = id_info.get('picture')

        if not email:
            raise HTTPException(status_code=400, detail="Invalid Google token: no email provided")

        async for db in get_db():
            # Check if user exists by email or google_id
            user = await db.fetchrow("SELECT * FROM users WHERE email = $1 OR google_id = $2", email, google_id)

            if user:
                # Link google_id if missing but email matched
                if not user['google_id'] or (picture and not user.get('avatar')):
                    await db.execute(
                        "UPDATE users SET google_id = $1, auth_provider = 'google', is_verified = true, avatar = COALESCE(avatar, $3) WHERE id = $2", 
                        google_id, user['id'], picture
                    )
                username = user['username']
            else:
                # Create a new user for Google login
                username = email.split('@')[0]
                # Check if username is taken, append suffix if so
                existing = await db.fetchrow("SELECT id FROM users WHERE username = $1", username)
                if existing:
                    username = f"{username}_{google_id[:4]}"
                
                is_admin = (email.lower() == 'sureshreigns220@gmail.com')
                    
                row = await db.fetchrow(
                    "INSERT INTO users (username, email, hashed_password, auth_provider, google_id, is_verified, is_admin, avatar) "
                    "VALUES ($1, $2, $3, 'google', $4, true, $5, $6) RETURNING id, username, email, is_admin",
                    username, email, "google_sso", google_id, is_admin, picture
                )
                user = dict(row)

            access_token = create_access_token(data={
                "sub": user['username'],
                "id": user['id'],
                "email": user['email'],
                "is_admin": user['is_admin']
            })
            set_auth_cookie(response, access_token)
        return {"access_token": access_token, "token_type": "bearer"}

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid Google token: {str(e)}")

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"success": True}
