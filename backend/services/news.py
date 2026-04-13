from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload  # 👈 добавить импорт

from core.websocket import manager
from db.models.news.news import News
from metrics.news import NEWS_CREATED, NEWS_DELETED, NEWS_FETCHED
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
            "news": {"id": str(news.id), "title": news.title, "excerpt": news.excerpt},
        }
    )
    return news


async def get_all_news(db: AsyncSession):
    NEWS_FETCHED.inc()
    # 👇 Подгружаем автора (JOIN или отдельный запрос)
    stmt = (
        select(News).options(selectinload(News.author)).order_by(News.created_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


async def get_news_by_id(db: AsyncSession, news_id: UUID):
    # 👇 Для одной новости тоже подгружаем автора
    stmt = select(News).where(News.id == news_id).options(selectinload(News.author))
    result = await db.execute(stmt)
    return result.scalar_one_or_none()  # scalar_one_or_none вместо scalar


async def delete_news(db: AsyncSession, news_id: UUID):
    news = await get_news_by_id(db, news_id)
    if news:
        await db.delete(news)
        await db.commit()
        NEWS_DELETED.inc()
    return news
