from typing import Optional
from uuid import UUID
from fastapi import HTTPException, status

from db.models.users import User
from repositories.users import UserRepository
from sqlalchemy.ext.asyncio import AsyncSession
from core.security import decode_access_token, get_password_hash, verify_password, create_access_token, create_refresh_token, decode_refresh_token
from schemas.token import Token
from schemas.users import UserCreate
from core.exceptions import CredentialsException
from redis.asyncio import Redis

class UserService:
    def __init__(self, session: AsyncSession, redis: Redis):
        self.session = session
        self.redis = redis
        self.repo = UserRepository(self.session)

    async def register(self, user_create: UserCreate) -> User:
        existing = await self.repo.get_by_email(user_create.email)
        if existing:
            raise CredentialsException("User already exists")
        return await self.repo.create(user_create)

    async def authenticate(self, email: str, password: str) -> Token:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise CredentialsException("Invalid credentials")
        
        access = create_access_token({"sub": str(user.id)})
        refresh = create_refresh_token(str(user.id))
        return Token(access_token=access, refresh_token=refresh)

    async def refresh_token(self, refresh_token: str) -> Token:
        payload = await decode_refresh_token(self.redis, refresh_token)
        user_id = UUID(payload["sub"])
        jti = payload["jti"]
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise CredentialsException("User not found")
        await self.redis.setex(f"blacklist:refresh:{jti}", 3600, "1")
        access = create_access_token({"sub": str(user.id)})
        new_refresh = create_refresh_token(str(user.id))
        return Token(access_token=access, refresh_token=new_refresh)

    async def logout(self, token: str):
        payload = await decode_access_token(self.redis, token)
        jti = payload.get("jti")
        if jti:
            await self.redis.setex(f"blacklist:access:{jti}", 900, "1")

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return await self.repo.get_by_id(user_id)
