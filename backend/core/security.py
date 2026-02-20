from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext
from redis.asyncio import Redis

from core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
REFRESH_TOKEN_EXPIRE_HOURS = settings.REFRESH_TOKEN_EXPIRE_HOURS

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "jti": str(uuid4())})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(subject: str) -> str:
    data = {"sub": subject}
    expire = datetime.now(timezone.utc) + timedelta(hours=REFRESH_TOKEN_EXPIRE_HOURS)
    data.update({"exp": expire, "jti": str(uuid4())})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

async def decode_access_token(redis_client: Redis, token: str) -> dict[str, Any]:
    if not token or not isinstance(token, str) or len(token.split('.')) != 3:
        raise JWTError("Invalid token format")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if await redis_client.exists(f"blacklist:access:{jti}"):
            raise JWTError("Access token revoked")
        return payload
    except (JWTError, jwt.JWTError):
        raise JWTError("Invalid or expired access token")

async def decode_refresh_token(redis_client: Redis, token: str) -> dict[str, Any]:
    if not token or not isinstance(token, str) or len(token.split('.')) != 3:
        raise JWTError("Invalid token format")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        jti = payload.get("jti")
        if await redis_client.exists(f"blacklist:refresh:{jti}"):
            raise JWTError("Refresh token revoked")
        return payload
    except (JWTError, jwt.JWTError):
        raise JWTError("Invalid or expired refresh token")
