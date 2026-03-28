from uuid import UUID

from db.models.news.news import News
from metrics.news import NEWS_CREATED, NEWS_DELETED, NEWS_FETCHED
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


async def create_news(db: AsyncSession, data):

    news = News(
        title=data.title,
        category=data.category,
        excerpt=data.excerpt,
        content=data.content,
        author_id=data.author,
    )

    db.add(news)

    await db.commit()
    await db.refresh(news)

    NEWS_CREATED.inc()

    return news


async def get_all_news(db: AsyncSession):

    NEWS_FETCHED.inc()

    result = await db.execute(select(News).order_by(News.created_at.desc()))

    return result.scalars().all()


async def get_news_by_id(db: AsyncSession, news_id: UUID):

    result = await db.execute(select(News).where(News.id == news_id))

    return result.scalar()


async def delete_news(db: AsyncSession, news_id: UUID):

    news = await get_news_by_id(db, news_id)

    if news:

        await db.delete(news)
        await db.commit()

        NEWS_DELETED.inc()

    return news
