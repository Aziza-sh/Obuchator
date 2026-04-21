from uuid import UUID
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user
from core.exceptions import NewsNotFoundException
from db.models.base import get_db
from db.models.users import User
from db.models.news.news_like import NewsLike

from schemas.news import NewsCreate, NewsResponse

from services.news import (
    create_news,
    delete_news,
    get_all_news,
    get_news_by_id,
)

from services.news_interactions import (
    add_view,
    like_news,
    unlike_news,
)

from metrics.news import NEWS_DELETED

router = APIRouter(prefix="/news", tags=["news"])


@router.post("/", response_model=NewsResponse)
async def create_news_endpoint(
    data: NewsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    news = await create_news(db, data, current_user.id)

    return {
        "id": news.id,
        "title": news.title,
        "category": news.category,
        "excerpt": news.excerpt,
        "content": news.content,
        "author_id": news.author_id,
        "created_at": news.created_at,
        "author": news.author,
        "likes_count": 0,
        "is_liked": False,
        "likes_count": 0,
        "views_count": 0, 
    }


@router.get("/", response_model=List[NewsResponse])
async def get_news_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    news_list = await get_all_news(db)

    result = []

    for news in news_list:

        likes_count = await db.scalar(
            select(func.count())
            .select_from(NewsLike)
            .where(NewsLike.news_id == news.id)
        )

        is_liked = await db.scalar(
            select(NewsLike).where(
                NewsLike.news_id == news.id,
                NewsLike.user_id == current_user.id,
            )
        )
        is_liked = is_liked is not None

        result.append(
            {
                "id": news.id,
                "title": news.title,
                "category": news.category,
                "excerpt": news.excerpt,
                "content": news.content,
                "author_id": news.author_id,
                "created_at": news.created_at,
                "author": news.author,
                "likes_count": likes_count or 0,
                "is_liked": is_liked,
                "views_count": 0,
            }
        )

    return result


@router.get("/{news_id}", response_model=NewsResponse)
async def get_single_news(
    news_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    news = await get_news_by_id(db, news_id)

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    likes_count = await db.scalar(
        select(func.count()).select_from(NewsLike).where(NewsLike.news_id == news.id)
    )

    is_liked = await db.scalar(
        select(NewsLike).where(
            NewsLike.news_id == news.id,
            NewsLike.user_id == current_user.id,
        )
    )
    is_liked = is_liked is not None

    return {
        "id": news.id,
        "title": news.title,
        "category": news.category,
        "excerpt": news.excerpt,
        "content": news.content,
        "author_id": news.author_id,
        "created_at": news.created_at,
        "author": news.author,
        "likes_count": likes_count or 0,
        "is_liked": is_liked,
        "views_count": getattr(news, "views_count", 0),
    }


@router.delete("/{news_id}")
async def delete_news_endpoint(
    news_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    news = await get_news_by_id(db, news_id)

    if not news:
        raise NewsNotFoundException(news_id)

    await delete_news(db, news_id)

    NEWS_DELETED.inc()

    return {"status": "deleted"}


@router.post("/{news_id}/like")
async def like_news_endpoint(
    news_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await like_news(db, news_id, current_user.id)


@router.delete("/{news_id}/like")
async def unlike_news_endpoint(
    news_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await unlike_news(db, news_id, current_user.id)


@router.post("/{news_id}/view")
async def view_news_endpoint(
    news_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await add_view(db, news_id, current_user.id)
