from __future__ import annotations

from typing import Optional
from uuid import UUID, uuid4

from db.models import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Импортируем модели, на которые ссылаемся (можно и не импортировать, если используем строки, но для ясности добавим)
# from db.models import User, News   # при необходимости


class NewsLike(Base):
    __tablename__ = "news_likes"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    news_id: Mapped[UUID] = mapped_column(ForeignKey("news.id"))

    # Связи
    # Используем строковые аннотации, чтобы избежать циклических импортов
    news: Mapped["News"] = relationship(back_populates="likes")
    # При необходимости добавить обратную связь с User: user: Mapped["User"] = relationship(back_populates="likes")
