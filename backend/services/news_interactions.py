from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from db.models.news.news_like import NewsLike
from db.models.news.news_view import NewsView


async def like_news(db: AsyncSession, news_id: UUID):

    query = select(NewsLike).where(NewsLike.news_id == news_id)

    result = await db.execute(query)

    existing = result.scalar_one_or_none()

    if existing:
        return {"message": "already liked"}

    like = NewsLike(news_id=news_id)

    db.add(like)

    await db.commit()

    return {"message": "liked"}


async def unlike_news(db: AsyncSession, news_id: UUID):

    query = select(NewsLike).where(NewsLike.news_id == news_id)

    result = await db.execute(query)

    like = result.scalar_one_or_none()

    if not like:
        return {"message": "like not found"}

    await db.delete(like)

    await db.commit()

    return {"message": "unliked"}


async def add_view(db: AsyncSession, news_id: UUID):

    view = NewsView(news_id=news_id)

    db.add(view)

    await db.commit()

    return {"message": "view counted"}
