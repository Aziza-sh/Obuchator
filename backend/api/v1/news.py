from uuid import UUID

from core.exceptions import NewsNotFoundException
from db.models.base import get_db
from fastapi import APIRouter, Depends, HTTPException
from metrics.news import NEWS_DELETED
from schemas.news import NewsCreate, NewsResponse
from services.news import create_news, delete_news, get_all_news, get_news_by_id
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/news", tags=["news"])


@router.post("/", response_model=NewsResponse)
async def create_news_endpoint(data: NewsCreate, db: AsyncSession = Depends(get_db)):

    return await create_news(db, data)


@router.get("/", response_model=list[NewsResponse])
async def get_news_endpoint(db: AsyncSession = Depends(get_db)):

    return await get_all_news(db)


@router.get("/{news_id}", response_model=NewsResponse)
async def get_single_news(news_id: UUID, db: AsyncSession = Depends(get_db)):

    news = await get_news_by_id(db, news_id)

    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    return news


async def delete_news(db: AsyncSession, news_id: UUID):

    news = await get_news_by_id(db, news_id)

    if not news:
        raise NewsNotFoundException(news_id)

    await db.delete(news)
    await db.commit()

    NEWS_DELETED.inc()

    return news
