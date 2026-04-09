from uuid import UUID

from api.deps import get_current_user
from core.exceptions import NewsNotFoundException
from db.models.base import get_db
from db.models.users import User
from fastapi import APIRouter, Depends, HTTPException
from metrics.news import NEWS_DELETED
from schemas.news import NewsCreate, NewsResponse
from services.news import create_news, delete_news, get_all_news, get_news_by_id
from services.news_interactions import add_view, like_news, unlike_news
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/news", tags=["news"])


@router.post("/", response_model=NewsResponse)
async def create_news_endpoint(
    data: NewsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    return await create_news(db, data, current_user.id)


@router.get("/", response_model=list[NewsResponse])
async def get_news_endpoint(db: AsyncSession = Depends(get_db)):

    return await get_all_news(db)


@router.get("/{news_id}", response_model=NewsResponse)
async def get_single_news(news_id: UUID, db: AsyncSession = Depends(get_db)):

    news = await get_news_by_id(db, news_id)

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return news


@router.delete("/{news_id}")
async def delete_news_endpoint(news_id: UUID, db: AsyncSession = Depends(get_db)):

    news = await get_news_by_id(db, news_id)

    if not news:
        raise NewsNotFoundException(news_id)

    await db.delete(news)
    await db.commit()

    NEWS_DELETED.inc()

    return await delete_news(db, news_id)


@router.post("/{news_id}/like")
async def like_news_endpoint(news_id: UUID, db: AsyncSession = Depends(get_db)):

    return await like_news(db, news_id)


@router.delete("/{news_id}/like")
async def unlike_news_endpoint(news_id: UUID, db: AsyncSession = Depends(get_db)):

    return await unlike_news(db, news_id)


@router.post("/{news_id}/view")
async def view_news_endpoint(news_id: UUID, db: AsyncSession = Depends(get_db)):

    return await add_view(db, news_id)
