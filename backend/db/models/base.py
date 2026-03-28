from core.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declarative_base

Base = declarative_base()

from db.models import *

engine = create_async_engine(settings.DATABASE_URL)

SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():

    async with SessionLocal() as session:
        yield session
