from typing import Optional
from uuid import UUID

from core.security import get_password_hash
from db.models.users import User
from schemas.users import UserCreate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_email(self, email: str) -> Optional[User]:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return await self.session.get(User, user_id)

    async def create(self, user_create: UserCreate) -> User:
        existing = await self.get_by_email(user_create.email)
        if existing:
            raise
        user = User(
            email=user_create.email,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            password_hash=get_password_hash(user_create.password),
        )
        self.session.add(user)
        await self.session.commit()
        return user
