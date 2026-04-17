from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.news.news import News
from db.models.news.news_like import NewsLike
from core.websocket import manager
from metrics.news import NEWS_FETCHED, NEWS_DELETED
from schemas.news import NewsCreate


async def create_news(db: AsyncSession, data: NewsCreate, author_id: UUID):
    news = News(
        title=data.title,
        category=data.category,
        excerpt=data.excerpt,
        content=data.content,
        author_id=author_id,
    )

    db.add(news)
    await db.commit()
    await db.refresh(news)

    await manager.broadcast(
        {
            "type": "news_created",
            "news": {
                "id": str(news.id),
                "title": news.title,
                "excerpt": news.excerpt,
            },
        }
    )

    return news


async def get_all_news(db: AsyncSession):
    NEWS_FETCHED.inc()

    stmt = (
        select(News).options(selectinload(News.author)).order_by(News.created_at.desc())
    )

    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_by_id(db: AsyncSession, news_id: UUID):
    stmt = select(News).where(News.id == news_id).options(selectinload(News.author))

    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_news(db: AsyncSession, news_id: UUID):
    news = await get_news_by_id(db, news_id)

    if not news:
        return None

    await db.delete(news)
    await db.commit()

    NEWS_DELETED.inc()

    return news
