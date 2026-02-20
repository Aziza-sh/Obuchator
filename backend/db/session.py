from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from core.config import settings

async_engine = create_async_engine(settings.DATABASE_URL)

async_session_local = async_sessionmaker(async_engine, expire_on_commit=False)

async def get_session():
    async with async_session_local() as session:
        async with session.begin():
            yield session
