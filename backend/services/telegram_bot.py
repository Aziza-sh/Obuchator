import asyncio
import logging
from typing import Optional
from uuid import UUID

import httpx
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings

logger = logging.getLogger(__name__)

_polling_task: Optional[asyncio.Task] = None
_http_client: Optional[httpx.AsyncClient] = None

_TG_API = "https://api.telegram.org/bot{token}/{method}"
_MATERIAL_TYPE_LABELS = {"homework": "Домашнее задание", "material": "Материал"}


def _url(method: str) -> str:
    return _TG_API.format(token=settings.TELEGRAM_BOT_TOKEN, method=method)


async def _send(method: str, **params) -> dict:
    if _http_client is None:
        return {}
    try:
        resp = await _http_client.post(_url(method), json=params, timeout=10)
        return resp.json()
    except Exception as e:
        logger.warning("Telegram API error (%s): %s", method, e)
        return {}


async def send_news_notification(chat_id: str, news_id: UUID, title: str, excerpt: str):
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    url = f"{settings.SITE_URL}/news_page.html?id={news_id}"
    text = f"📰 <b>{title}</b>\n\n{excerpt}\n\n<a href=\"{url}\">Читать полностью →</a>"
    await _send("sendMessage", chat_id=int(chat_id), text=text, parse_mode="HTML",
                disable_web_page_preview=True)


async def send_course_notification(
    chat_id: str,
    course_id: UUID,
    course_name: str,
    material_title: str,
    material_type: str,
):
    if not settings.TELEGRAM_BOT_TOKEN:
        return
    type_label = _MATERIAL_TYPE_LABELS.get(material_type, "Материал")
    url = f"{settings.SITE_URL}/course_page.html?id={course_id}"
    text = (
        f"📚 Обновление в курсе <b>\"{course_name}\"</b>\n\n"
        f"{type_label}: <b>{material_title}</b>\n\n"
        f"<a href=\"{url}\">Перейти к курсу →</a>"
    )
    await _send("sendMessage", chat_id=int(chat_id), text=text, parse_mode="HTML",
                disable_web_page_preview=True)


async def _handle_update(update: dict, redis: Redis, session_factory):
    message = update.get("message") or update.get("channel_post")
    if not message:
        return

    text: str = message.get("text", "")
    chat_id = str(message["chat"]["id"])

    if not text.startswith("/start"):
        return

    parts = text.split(maxsplit=1)
    token = parts[1].strip() if len(parts) > 1 else ""

    if not token:
        await _send(
            "sendMessage",
            chat_id=int(chat_id),
            text=(
                "Привет! Я бот для уведомлений платформы Обучатор.\n"
                "Чтобы привязать аккаунт, перейдите в настройки профиля на сайте."
            ),
        )
        return

    user_id_str = await redis.get(f"tg_link:{token}")
    if not user_id_str:
        await _send(
            "sendMessage",
            chat_id=int(chat_id),
            text="Ссылка недействительна или истекла. Запросите новую на сайте.",
        )
        return

    from db.models.users import User

    async with session_factory() as session:
        async with session.begin():
            result = await session.execute(
                select(User).where(User.id == UUID(user_id_str))
            )
            user = result.scalar_one_or_none()
            if not user:
                await _send("sendMessage", chat_id=int(chat_id), text="Пользователь не найден.")
                return

            user.telegram_chat_id = chat_id

    await redis.delete(f"tg_link:{token}")
    await _send(
        "sendMessage",
        chat_id=int(chat_id),
        text=f"Аккаунт успешно привязан! Добро пожаловать, {user.first_name}! "
             "Теперь вы будете получать уведомления.",
    )


async def _poll_loop(redis: Redis, session_factory):
    offset = 0
    logger.info("Telegram bot long-polling started")
    while True:
        try:
            resp = await _http_client.get(
                _url("getUpdates"),
                params={"offset": offset, "timeout": 25, "allowed_updates": ["message"]},
                timeout=30,
            )
            data = resp.json()
            if not data.get("ok"):
                await asyncio.sleep(5)
                continue

            for update in data.get("result", []):
                offset = update["update_id"] + 1
                try:
                    await _handle_update(update, redis, session_factory)
                except Exception as e:
                    logger.error("Error handling update: %s", e)

        except asyncio.CancelledError:
            logger.info("Telegram polling cancelled")
            return
        except Exception as e:
            logger.error("Polling error: %s", e)
            await asyncio.sleep(5)


async def start_polling(redis: Redis, session_factory):
    global _http_client, _polling_task
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set — Telegram bot disabled")
        return

    _http_client = httpx.AsyncClient()
    _polling_task = asyncio.create_task(_poll_loop(redis, session_factory))


async def stop_polling():
    global _http_client, _polling_task
    if _polling_task:
        _polling_task.cancel()
        try:
            await _polling_task
        except asyncio.CancelledError:
            pass
    if _http_client:
        await _http_client.aclose()
    logger.info("Telegram bot stopped")
