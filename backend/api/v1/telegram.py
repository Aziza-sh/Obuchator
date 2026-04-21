import secrets

from fastapi import APIRouter, Depends
from redis.asyncio import Redis
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import get_current_user, get_redis
from core.config import settings
from db.models.base import get_db
from db.models.users import User

router = APIRouter(prefix="/api/v1/telegram", tags=["telegram"])


@router.post("/link-token")
async def generate_link_token(
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    token = secrets.token_urlsafe(32)
    await redis.setex(
        f"tg_link:{token}",
        settings.TELEGRAM_LINK_TOKEN_EXPIRE_SECONDS,
        str(current_user.id),
    )
    return {"token": token, "expires_in": settings.TELEGRAM_LINK_TOKEN_EXPIRE_SECONDS}


@router.delete("/unlink")
async def unlink_telegram(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(User).where(User.id == current_user.id).values(telegram_chat_id=None)
    )
    await db.commit()
    return {"status": "unlinked"}


@router.get("/status")
async def telegram_status(current_user: User = Depends(get_current_user)):
    return {"linked": current_user.telegram_chat_id is not None}
