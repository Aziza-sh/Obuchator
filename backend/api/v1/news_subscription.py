from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user
from db.models.base import get_db
from db.models.news.news_sub import NewsSubscription
from db.models.users import User

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/subscribe")
async def get_subscription_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await db.scalar(
        select(NewsSubscription).where(NewsSubscription.user_id == current_user.id)
    )
    return {
        "subscribed": sub is not None,
        "telegram_linked": current_user.telegram_chat_id is not None,
    }


@router.post("/subscribe")
async def subscribe_to_news(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    try:
        db.add(NewsSubscription(user_id=current_user.id))
        await db.commit()
        return {"status": "subscribed"}
    except IntegrityError:
        await db.rollback()
        return {"status": "already_subscribed"}


@router.delete("/subscribe")
async def unsubscribe_from_news(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await db.scalar(
        select(NewsSubscription).where(NewsSubscription.user_id == current_user.id)
    )
    if not sub:
        return {"status": "not_subscribed"}

    await db.delete(sub)
    await db.commit()
    return {"status": "unsubscribed"}
