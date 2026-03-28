from __future__ import annotations

from uuid import UUID, uuid4

from db.models import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class NewsSubscription(Base):
    __tablename__ = "news_subscriptions"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    news_id: Mapped[UUID] = mapped_column(ForeignKey("news.id"))
    # Если нужна связь с User, добавьте:
    # user: Mapped["User"] = relationship(back_populates="subscriptions")
