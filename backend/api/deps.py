from typing import Annotated, AsyncGenerator
from uuid import UUID

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from core.config import settings
from core.exceptions import CredentialsException
from db.session import get_session
from db.models.users import User
from services.users import UserService
from core.security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

async def get_redis() -> AsyncGenerator[Redis, None]:
    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield redis
    finally:
        await redis.close()

def get_user_service(
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis)
) -> UserService:
    return UserService(session=session, redis=redis)

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    service: Annotated[UserService, Depends(get_user_service)]
) -> User:
    try:
        payload = await decode_access_token(service.redis, token)
        user_id_str: str | None = payload.get("sub")
        if user_id_str is None:
            raise CredentialsException
        user_id = UUID(user_id_str)
    except (JWTError, ValueError, CredentialsException):
        raise CredentialsException

    user = await service.get_by_id(user_id)
    if not user:
        raise CredentialsException
    return user
