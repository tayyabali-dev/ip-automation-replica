from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from app.core import security
from app.core.config import settings
from app.db.mongodb import get_database
from app.api import deps
from app.models.user import UserCreate, UserResponse, UserInDB
from app.services.audit import audit_service
from motor.motor_asyncio import AsyncIOMotorDatabase
from pydantic import BaseModel
from bson import ObjectId

router = APIRouter()

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@router.post("/login", response_model=Token)
async def login_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = await db.users.find_one({"email": form_data.username})
    if not user or not security.verify_password(form_data.password, user["hashed_password"]):
        # Log failure (if user exists, use ID, else None/System)
        user_id = str(user["_id"]) if user else "unauthenticated"
        await audit_service.log_event(
            user_id=user_id,
            event_type="login_failure",
            details={"email": form_data.username}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Token Claims
    token_data = {
        "sub": str(user["_id"]),
        "email": user["email"],
        "name": user["full_name"],
        "role": user["role"],
        "firm": user.get("firm_affiliation")
    }
    
    access_token = security.create_access_token(
        data=token_data, expires_delta=access_token_expires
    )
    
    refresh_token = security.create_refresh_token(
        data={"sub": str(user["_id"])}
    )
    
    await audit_service.log_event(
        user_id=str(user["_id"]),
        event_type="login_success",
        details={"email": user["email"]}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }

@router.post("/seed-user", status_code=201)
async def seed_user(
    user_in: UserCreate,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """
    Temporary endpoint to seed users for MVP since registration is not required
    """
    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User with this email already exists"
        )
        
    hashed_password = security.get_password_hash(user_in.password)
    user_db = UserInDB(
        **user_in.model_dump(),
        hashed_password=hashed_password
    )
    
    new_user = await db.users.insert_one(user_db.model_dump(by_alias=True))
    created_user = await db.users.find_one({"_id": new_user.inserted_id})
    
    return UserResponse(**created_user)

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: UserResponse = Depends(deps.get_current_user)
) -> Any:
    """
    Get current user information
    """
    return current_user

@router.post("/logout")
async def logout(
    current_user: UserResponse = Depends(deps.get_current_user)
) -> Any:
    """
    Logout endpoint (for audit logging)
    """
    await audit_service.log_event(
        user_id=str(current_user.id),
        event_type="logout",
        details={"email": current_user.email}
    )
    return {"message": "Successfully logged out"}

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: AsyncIOMotorDatabase = Depends(get_database)
) -> Any:
    """
    Exchange a valid refresh token for a new access token.
    Also issues a new refresh token (token rotation for security).
    """
    try:
        # Decode the refresh token
        payload = jwt.decode(
            request.refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Verify it's a refresh token (not an access token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Check expiration (jose does this automatically, but explicit check)
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token expired"
            )
        
        # Get user ID from token
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Verify user still exists and is active
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled"
            )
        
        # Issue new tokens (token rotation)
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Token Claims for access token
        token_data = {
            "sub": str(user["_id"]),
            "email": user["email"],
            "name": user["full_name"],
            "role": user["role"],
            "firm": user.get("firm_affiliation")
        }
        
        new_access_token = security.create_access_token(
            data=token_data, expires_delta=access_token_expires
        )
        new_refresh_token = security.create_refresh_token(
            data={"sub": str(user["_id"])}
        )
        
        # Log the token refresh event
        await audit_service.log_event(
            user_id=str(user["_id"]),
            event_type="token_refresh",
            details={"email": user["email"]}
        )
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
        
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )