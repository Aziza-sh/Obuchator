from uuid import UUID

from db.models.news.news_like import NewsLike
from db.models.news.news_view import NewsView
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


async def like_news(db: AsyncSession, news_id: UUID, user_id: UUID):
    result = await db.execute(
        select(NewsLike).where(
            NewsLike.user_id == user_id,
            NewsLike.news_id == news_id,
        )
    )

    existing = result.scalars().first()

    if existing:
        return {"message": "Already liked"}

    like = NewsLike(user_id=user_id, news_id=news_id)
    db.add(like)
    await db.commit()

    return {"message": "Liked"}


async def unlike_news(db: AsyncSession, news_id: UUID, user_id: UUID):
    result = await db.execute(
        select(NewsLike).where(
            NewsLike.news_id == news_id,
            NewsLike.user_id == user_id,
        )
    )

    like = result.scalars().first()

    if not like:
        return {"message": "like not found"}

    await db.delete(like)
    await db.commit()

    return {"message": "unliked"}


from sqlalchemy import select


async def add_view(db: AsyncSession, news_id: UUID, user_id: UUID):
    existing = await db.scalar(
        select(NewsView).where(NewsView.news_id == news_id, NewsView.user_id == user_id)
    )
    if existing:
        return {"message": "already viewed"}

    view = NewsView(news_id=news_id, user_id=user_id)
    db.add(view)
    await db.commit()
    return {"message": "view counted"}


async def get_likes_count(db: AsyncSession, news_id: UUID) -> int:
    result = await db.execute(
        select(func.count()).select_from(NewsLike).where(NewsLike.news_id == news_id)
    )
    return result.scalar_one()
