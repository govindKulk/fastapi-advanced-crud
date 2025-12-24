from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core import security
from app.core.config import settings
from app.crud.user import user as crud_user
from app.models.user import UserCreate, UserResponse, UserLogin
from app.models.database import User


router = APIRouter()

@router.post("/login")
async def login(
    *,
    db: AsyncSession = Depends(deps.get_db),
    credentials: UserLogin,
    response: Response
) -> Any:
    """
    Simple JSON login endpoint - accepts username and password as JSON
    """
    user = await crud_user.authenticate(
        db, username=credentials.username, password=credentials.password
    )
    if not user:
        raise HTTPException(
            status_code=401, 
            detail="Incorrect username or password"
        )
    elif not crud_user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.username, expires_delta=access_token_expires
    )


    refresh_token = await security.create_refresh_token(
        subject=str(user.id), db=db
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,

    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/login/access-token")
async def login_access_token(
    db: AsyncSession = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login (for Swagger UI authorization).
    This endpoint uses form data (application/x-www-form-urlencoded).
    Use the /login endpoint for JSON requests.
    """
    user = await crud_user.authenticate(
        db, username=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    elif not crud_user.is_active(user):
        raise HTTPException(status_code=400, detail="Inactive user")
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.username, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }

@router.post("/register", response_model=UserResponse, status_code=201)
async def create_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = await crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system."
        )
    user = await crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system."
        )
    user = await crud_user.create(db, obj_in=user_in)
    return user

@router.get("/me", response_model=UserResponse)
async def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str





@router.get("/refresh", response_model = TokenRefreshResponse)
async def refresh_token(
    request: Request,
    response: Response,
    current_user: User = Depends(deps.get_current_active_user),
    db: AsyncSession = Depends(deps.get_db)
) -> Any:
    """
    Refresh access token for current user.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        current_user.username, expires_delta=access_token_expires
    )

    rt_string = request.cookies.get("refresh_token")
    if not rt_string:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    
    rt = await security.verify_refresh_token(
        token=rt_string, db=db
    )

    if rt is None or rt.user_id != current_user.id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")    
    

    new_refresh_token = await security.create_refresh_token(
        subject=str(current_user.id), db=db, old_rt=rt )
    
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Logout user by clearing the refresh token cookie.
    """
    rt_str = request.cookies.get("refresh_token")
    if not rt_str:
        raise HTTPException(status_code=401, detail="Refresh token missing")
    

    rt = await security.verify_refresh_token(
        token=rt_str, db=db
    )

    if rt is None or rt.revoked:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    rt.revoked = True
    await db.commit()
    response.delete_cookie(key="refresh_token")
    return {"msg": "Successfully logged out"}
