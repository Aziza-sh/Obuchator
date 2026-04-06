from uuid import UUID

from schemas.news import NewsCreate
from db.models.news.news import News
from metrics.news import NEWS_CREATED, NEWS_DELETED, NEWS_FETCHED
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.websocket import manager

async def create_news(db: AsyncSession, data: NewsCreate, author_id: UUID):

    news = News(
        title=data.title,
        category=data.category,
        excerpt=data.excerpt,
        content=data.content,
        author_id=author_id
    )

    db.add(news)
    await db.commit()
    await db.refresh(news)

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


async def create_news(db: AsyncSession, data: NewsCreate, author_id):

    news = News(
        title=data.title,
        category=data.category,
        excerpt=data.excerpt,
        content=data.content,
        author_id=author_id
    )

    db.add(news)
    await db.commit()
    await db.refresh(news)

    await manager.broadcast({
        "type": "news_created",
        "news": {
            "id": str(news.id),
            "title": news.title,
            "excerpt": news.excerpt
        }
    })

    return news