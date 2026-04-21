from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from db.models.news.news import News
from db.models.news.news_like import NewsLike
from db.models.news.news_sub import NewsSubscription
from db.models.news.news_view import NewsView
from db.models.users import User
from core.websocket import manager
from metrics.news import NEWS_FETCHED, NEWS_DELETED
from schemas.news import NewsCreate
from services.telegram_bot import send_news_notification


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

    stmt = select(News).where(News.id == news.id).options(selectinload(News.author))
    result = await db.execute(stmt)
    news_with_author = result.scalar_one()
    news_with_author.views_count = 0

    await manager.broadcast(
        {
            "type": "news_created",
            "news": {
                "id": str(news_with_author.id),
                "title": news_with_author.title,
                "excerpt": news_with_author.excerpt,
            },
        }
    )

    # Notify Telegram subscribers
    subs_stmt = select(NewsSubscription).options(selectinload(NewsSubscription.user))
    subs_result = await db.execute(subs_stmt)
    subscriptions = subs_result.scalars().all()

    for sub in subscriptions:
        if sub.user and sub.user.telegram_chat_id:
            await send_news_notification(
                chat_id=sub.user.telegram_chat_id,
                news_id=news_with_author.id,
                title=news_with_author.title,
                excerpt=news_with_author.excerpt,
            )

    return news_with_author


async def get_all_news(db: AsyncSession):
    NEWS_FETCHED.inc()

    subq = (
        select(NewsView.news_id, func.count().label("views_count"))
        .group_by(NewsView.news_id)
        .subquery()
    )
    stmt = (
        select(News, func.coalesce(subq.c.views_count, 0).label("views_count"))
        .outerjoin(subq, News.id == subq.c.news_id)
        .options(selectinload(News.author))
        .order_by(News.created_at.desc())
    )
    result = await db.execute(stmt)
    rows = result.all()
    for news, views_count in rows:
        news.views_count = views_count
    return [row[0] for row in rows]


async def get_news_by_id(db: AsyncSession, news_id: UUID):
    stmt = select(News).where(News.id == news_id).options(selectinload(News.author))
    result = await db.execute(stmt)
    news = result.scalar_one_or_none()
    if news:
        views_stmt = select(func.count()).where(NewsView.news_id == news_id)
        views_count = await db.scalar(views_stmt)
        news.views_count = views_count or 0
    return news


async def delete_news(db: AsyncSession, news_id: UUID):
    news = await get_news_by_id(db, news_id)
    if not news:
        return None
    await db.delete(news)
    await db.commit()
    NEWS_DELETED.inc()
    return news
