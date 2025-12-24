from datetime import datetime, timedelta, timezone
from typing import Any, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings
import uuid
from app.models.database import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

async def create_refresh_token(subject: str, db: AsyncSession, old_rt: RefreshToken | None = None) -> str:
    try:
        if old_rt:
            # Revoke the old refresh token
            old_rt.revoked = True
            await db.commit()
        
        jti = str(uuid.uuid4())

        # Use timezone-aware datetime
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode : dict[str, Any] = {"exp": expire, "sub": str(subject), "jti": jti}

        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)

        rt = RefreshToken(
            jti=jti,
            user_id=int(subject),
            expiry_date=expire,
            revoked=False
        )
        db.add(rt)
        await db.commit()
        
        return encoded_jwt
    
    except Exception as e:
        await db.rollback()
        print("Error creating refresh token: ", e)
        raise e
    
async def verify_refresh_token(token: str, db: AsyncSession) -> Union[RefreshToken, None]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        jti: Any = payload.get("jti")
        user_id: Any = payload.get("sub")
        if jti is None or user_id is None:
            return None
        
        rt = await db.get(RefreshToken, jti)
        # Fix: Use timezone-aware datetime for comparison
        if rt is None or rt.revoked or rt.expiry_date < datetime.now(timezone.utc):
            return None
        
        return rt
    except JWTError:
        return None

def create_access_token(
    subject: Union[str, Any], expires_delta: timedelta | None = None
) -> str:
    if expires_delta:
        # Use timezone-aware datetime
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode : dict[str, Any] = {"exp": expire, "sub": str(subject)}

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_token(token: str) -> Union[str, None]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        print("Payload: ", payload)
        return payload.get("sub")
    except JWTError:
        return None
